from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from config import get_db
from models.database import User, RecommendationHistory, UserProfile as UserProfileDB
from models.schemas import UserProfileResponse, UserProfileUpdate
from services.auth_service import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
)

auth_router = APIRouter(prefix="/api/auth", tags=["authentication"])


class RegisterRequest(BaseModel):
    email: EmailStr
    username: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    username: str


class UserResponse(BaseModel):
    id: int
    email: str
    username: str


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
        profile.buget is not None,
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

    # Creează profil gol asociat
    profile = UserProfileDB(user_id=user.id)
    db.add(profile)
    db.commit()

    token = create_access_token({"sub": user.id})
    return TokenResponse(access_token=token, token_type="bearer", username=user.username)


@auth_router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Email sau parola incorecta")
    token = create_access_token({"sub": user.id})
    return TokenResponse(access_token=token, token_type="bearer", username=user.username)


@auth_router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse(
        id=current_user.id, email=current_user.email, username=current_user.username
    )


@auth_router.get("/profile", response_model=UserProfileResponse)
def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Returnează profilul persistent. Creează unul gol dacă nu există încă."""
    profile = _get_or_create_profile(current_user.id, db)
    return _profile_to_response(profile)


@auth_router.put("/profile", response_model=UserProfileResponse)
def update_profile(
    update: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Actualizare parțială: doar câmpurile trimise se modifică."""
    profile = _get_or_create_profile(current_user.id, db)

    update_data = update.model_dump(exclude_unset=True)

    # Marchează test completat dacă s-au trimis scoruri comportamentale
    test_fields = {"score_comfort", "score_sport", "score_siguranta", "score_economie", "score_estetica"}
    if any(f in update_data for f in test_fields):
        profile.has_completed_test = True

    for field, value in update_data.items():
        setattr(profile, field, value)

    db.commit()
    db.refresh(profile)
    return _profile_to_response(profile)


@auth_router.get("/history")
def get_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
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
