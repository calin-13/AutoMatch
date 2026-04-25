from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from config import get_db
from models.database import User, RecommendationHistory
from services.auth_service import hash_password, verify_password, create_access_token, get_current_user

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
    return UserResponse(id=current_user.id, email=current_user.email, username=current_user.username)


@auth_router.get("/history")
def get_history(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    history = db.query(RecommendationHistory).filter(
        RecommendationHistory.user_id == current_user.id
    ).order_by(RecommendationHistory.created_at.desc()).all()

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
        ]
    }
