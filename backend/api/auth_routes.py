from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from slowapi import Limiter
from slowapi.util import get_remote_address
from config import get_db, LOGIN_RATE_LIMIT, FRONTEND_URL, RESET_TOKEN_EXPIRE_MINUTES
from models.database import (
    User, RecommendationHistory, UserProfile as UserProfileDB,
    Recommendation, RecommendationItem, Car
)
from models.schemas import (
    UserProfileResponse, UserProfileUpdate,
    RecommendationListResponse, RecommendationListItem,
    RecommendationDetailResponse, RecommendationItemDetail,
)
from services.auth_service import (
    hash_password, verify_password, create_access_token, get_current_user,
    generate_reset_token, hash_reset_token,
)
from services.email_service import send_password_reset_email

auth_router = APIRouter(prefix="/api/auth", tags=["authentication"])

limiter = Limiter(key_func=get_remote_address)


class RegisterRequest(BaseModel):
    email: EmailStr
    username: str
    role: str = "user"
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    username: str
    role: str = "user"


class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    role: str = "user"


def _get_or_create_profile(user_id: int, db: Session) -> UserProfileDB:
    profile = db.query(UserProfileDB).filter(UserProfileDB.user_id == user_id).first()
    if profile is None:
        profile = UserProfileDB(user_id=user_id)
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile


def _profile_to_response(profile: UserProfileDB) -> UserProfileResponse:
    is_complete = all([
        profile.inaltime is not None,
        profile.greutate is not None,
        profile.km_zi is not None,
        profile.tip_combustibil is not None,
        profile.has_completed_test,
    ])
    return UserProfileResponse(
        id=profile.id,
        user_id=profile.user_id,
        inaltime=profile.inaltime,
        greutate=profile.greutate,
        buget=profile.buget,
        km_zi=profile.km_zi,
        tip_combustibil=profile.tip_combustibil,
        score_comfort=profile.score_comfort,
        score_sport=profile.score_sport,
        score_siguranta=profile.score_siguranta,
        score_economie=profile.score_economie,
        score_estetica=profile.score_estetica,
        has_completed_test=profile.has_completed_test,
        test_version_completed=profile.test_version_completed,
        is_complete=is_complete,
    )


@auth_router.post("/register", response_model=TokenResponse)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == req.email).first():
        raise HTTPException(status_code=400, detail="Email deja inregistrat")
    if db.query(User).filter(User.username == req.username).first():
        raise HTTPException(status_code=400, detail="Username deja folosit")

    user = User(
        email=req.email,
        username=req.username,
        hashed_password=hash_password(req.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    profile = UserProfileDB(user_id=user.id)
    db.add(profile)
    db.commit()

    token = create_access_token({"sub": user.id})
    return TokenResponse(access_token=token, token_type="bearer", username=user.username)


@auth_router.post("/login", response_model=TokenResponse)
@limiter.limit(LOGIN_RATE_LIMIT)
def login(request: Request, req: LoginRequest, db: Session = Depends(get_db)):
    """Rate-limited la valoarea din LOGIN_RATE_LIMIT (default: 5/minute per IP)."""
    user = db.query(User).filter(User.email == req.email).first()
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Email sau parola incorecta")
    token = create_access_token({"sub": user.id})
    return TokenResponse(access_token=token, token_type="bearer", username=user.username)


@auth_router.post("/forgot-password")
@limiter.limit("3/minute")
def forgot_password(request: Request, req: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()
    if user is not None:
        raw, token_hash = generate_reset_token()
        user.reset_token_hash = token_hash
        user.reset_token_expires = datetime.now(timezone.utc) + timedelta(minutes=RESET_TOKEN_EXPIRE_MINUTES)
        db.commit()
        reset_link = f"{FRONTEND_URL}/reset-password?token={raw}"
        send_password_reset_email(user.email, reset_link)
    return {"message": "Daca exista un cont cu acest email, am trimis un link de resetare."}


@auth_router.post("/reset-password")
@limiter.limit("5/minute")
def reset_password(request: Request, req: ResetPasswordRequest, db: Session = Depends(get_db)):
    if len(req.new_password) < 6:
        raise HTTPException(status_code=400, detail="Parola trebuie sa aiba minim 6 caractere")
    token_hash = hash_reset_token(req.token)
    user = db.query(User).filter(User.reset_token_hash == token_hash).first()
    if user is None or user.reset_token_expires is None:
        raise HTTPException(status_code=400, detail="Link invalid sau expirat")
    expires = user.reset_token_expires
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=timezone.utc)
    if expires < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Link invalid sau expirat")
    user.hashed_password = hash_password(req.new_password)
    user.reset_token_hash = None
    user.reset_token_expires = None
    db.commit()
    return {"message": "Parola a fost resetata. Te poti autentifica acum."}


@auth_router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse(
        id=current_user.id, email=current_user.email, username=current_user.username, role=current_user.role
    )


@auth_router.get("/profile", response_model=UserProfileResponse)
def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = _get_or_create_profile(current_user.id, db)
    return _profile_to_response(profile)


@auth_router.put("/profile", response_model=UserProfileResponse)
def update_profile(
    update: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = _get_or_create_profile(current_user.id, db)
    update_data = update.model_dump(exclude_unset=True)

    test_fields = {"score_comfort", "score_sport", "score_siguranta", "score_economie", "score_estetica"}
    if any(f in update_data for f in test_fields):
        profile.has_completed_test = True

    for field, value in update_data.items():
        setattr(profile, field, value)

    db.commit()
    db.refresh(profile)
    return _profile_to_response(profile)


@auth_router.get(
    "/history",
    deprecated=True,
    summary="DEPRECATED: foloseste GET /api/auth/recommendations",
)
def get_history_legacy(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    history = (
        db.query(RecommendationHistory)
        .filter(RecommendationHistory.user_id == current_user.id)
        .order_by(RecommendationHistory.created_at.desc())
        .all()
    )
    return {
        "total": len(history),
        "history": [
            {
                "id": h.id,
                "buget": h.buget,
                "tip_combustibil": h.tip_combustibil,
                "recommended_cars": h.recommended_cars,
                "created_at": h.created_at.isoformat() if h.created_at else None,
            }
            for h in history
        ],
    }


@auth_router.get(
    "/recommendations",
    response_model=RecommendationListResponse,
)
def list_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    recs = (
        db.query(Recommendation)
        .filter(Recommendation.user_id == current_user.id)
        .order_by(Recommendation.created_at.desc())
        .all()
    )

    items = []
    for r in recs:
        top_item = r.items[0] if r.items else None
        top_marca = None
        top_model = None
        top_score = None
        if top_item is not None:
            car = db.query(Car).filter(Car.id == top_item.car_id).first()
            if car is not None:
                top_marca = car.marca
                top_model = car.model
            top_score = top_item.score_total

        items.append(RecommendationListItem(
            id=r.id,
            scoring_method=r.scoring_method,
            has_feedback_reranking=r.has_feedback_reranking,
            items_count=len(r.items),
            top_car_marca=top_marca,
            top_car_model=top_model,
            top_score=top_score,
            created_at=r.created_at,
        ))

    return RecommendationListResponse(total=len(items), recommendations=items)


@auth_router.get(
    "/recommendations/{rec_id}",
    response_model=RecommendationDetailResponse,
)
def get_recommendation_detail(
    rec_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    rec = (
        db.query(Recommendation)
        .filter(Recommendation.id == rec_id, Recommendation.user_id == current_user.id)
        .first()
    )
    if rec is None:
        raise HTTPException(
            status_code=404,
            detail="Recomandarea nu exista sau nu apartine acestui utilizator",
        )

    items_detail = []
    for item in rec.items:
        car = db.query(Car).filter(Car.id == item.car_id).first()
        if car is None:
            continue
        items_detail.append(RecommendationItemDetail(
            rank=item.rank,
            car_id=car.id,
            marca=car.marca,
            model=car.model,
            an=car.an,
            pret=car.pret,
            tip_combustibil=car.tip_combustibil,
            tip_caroserie=car.tip_caroserie,
            score_total=item.score_total,
            score_details=item.score_details or {},
        ))

    return RecommendationDetailResponse(
        id=rec.id,
        user_id=rec.user_id,
        profile_snapshot=rec.profile_snapshot,
        scoring_method=rec.scoring_method,
        has_feedback_reranking=rec.has_feedback_reranking,
        total_candidates=rec.total_candidates,
        created_at=rec.created_at,
        items=items_detail,
    )
