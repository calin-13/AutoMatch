from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class PhysiologicalData(BaseModel):
    """Date ergonomice/practice ale utilizatorului."""
    inaltime: float = Field(..., description="Înălțimea în cm", ge=140, le=220)
    greutate: float = Field(..., description="Greutatea în kg", ge=40, le=200)
    buget: float = Field(..., description="Bugetul în EUR", ge=1000, le=500000)
    km_zi: float = Field(..., description="Km parcurși pe zi", ge=0, le=500)
    tip_combustibil: str = Field(..., description="benzina/diesel/electric/hybrid")


class BehavioralScores(BaseModel):
    """Scorurile din mini-testul comportamental."""
    comfort: float = Field(default=0, ge=0, le=15)
    sport: float = Field(default=0, ge=0, le=15)
    siguranta: float = Field(default=0, ge=0, le=15)
    economie: float = Field(default=0, ge=0, le=15)
    estetica: float = Field(default=0, ge=0, le=15)


class UserInput(BaseModel):
    physiological: PhysiologicalData
    behavioral: BehavioralScores


class CarRecommendation(BaseModel):
    id: int
    marca: str
    model: str
    an: int
    pret: float
    tip_combustibil: str
    tip_caroserie: str
    score_total: float = Field(..., description="Scor de potrivire 0-100")
    score_details: dict = Field(default_factory=dict)


class UserProfile(BaseModel):
    """Profilul calculat al utilizatorului (preferințe normalizate)."""
    comfort: float
    sport: float
    siguranta: float
    economie: float
    estetica: float
    categorie_buget: str
    categorie_utilizare: str


class RecommendationResponse(BaseModel):
    recommendations: list[CarRecommendation]
    user_profile: UserProfile
    recommendation_id: Optional[int] = Field(
        default=None,
        description="ID-ul intrării din istoric (doar pentru endpoint-urile autentificate). Folosit la trimiterea feedback-ului.",
    )


# === Profil persistent ===

class UserProfileResponse(BaseModel):
    id: int
    user_id: int
    inaltime: Optional[float] = None
    greutate: Optional[float] = None
    buget: Optional[float] = None
    km_zi: Optional[float] = None
    tip_combustibil: Optional[str] = None
    score_comfort: Optional[float] = None
    score_sport: Optional[float] = None
    score_siguranta: Optional[float] = None
    score_economie: Optional[float] = None
    score_estetica: Optional[float] = None
    has_completed_test: bool = False
    is_complete: bool = False

    class Config:
        from_attributes = True


class UserProfileUpdate(BaseModel):
    inaltime: Optional[float] = Field(None, ge=140, le=220)
    greutate: Optional[float] = Field(None, ge=40, le=200)
    buget: Optional[float] = Field(None, ge=1000, le=500000)
    km_zi: Optional[float] = Field(None, ge=0, le=500)
    tip_combustibil: Optional[str] = None
    score_comfort: Optional[float] = Field(None, ge=0, le=15)
    score_sport: Optional[float] = Field(None, ge=0, le=15)
    score_siguranta: Optional[float] = Field(None, ge=0, le=15)
    score_economie: Optional[float] = Field(None, ge=0, le=15)
    score_estetica: Optional[float] = Field(None, ge=0, le=15)


# === Feedback ===

class FeedbackCreate(BaseModel):
    """Trimitere feedback pentru o mașină recomandată."""
    car_id: int = Field(..., description="ID-ul mașinii pentru care se dă feedback")
    rating: int = Field(..., ge=-1, le=1, description="-1 (dislike), 0 (neutru), +1 (like)")
    recommendation_id: Optional[int] = Field(
        default=None,
        description="ID-ul intrării din istoric (opțional). Permite analiză contextuală.",
    )
    comment: Optional[str] = Field(default=None, max_length=500)


class FeedbackResponse(BaseModel):
    id: int
    user_id: int
    car_id: int
    recommendation_id: Optional[int] = None
    rating: int
    comment: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FeedbackHistoryItem(BaseModel):
    """Feedback cu detalii despre mașină asociată."""
    id: int
    car_id: int
    car_marca: str
    car_model: str
    car_an: int
    rating: int
    comment: Optional[str] = None
    recommendation_id: Optional[int] = None
    created_at: datetime


class FeedbackStatsItem(BaseModel):
    """Statistici agregate per mașină."""
    car_id: int
    marca: str
    model: str
    likes: int
    dislikes: int
    neutral: int
    total: int
    score: float = Field(..., description="(likes - dislikes) / total")


class FeedbackStatsResponse(BaseModel):
    total_feedbacks: int
    most_liked: list[FeedbackStatsItem]
    most_disliked: list[FeedbackStatsItem]
