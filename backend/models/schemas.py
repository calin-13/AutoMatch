from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class PhysiologicalData(BaseModel):
    inaltime: float = Field(..., description="Înălțimea în cm", ge=140, le=220)
    greutate: float = Field(..., description="Greutatea în kg", ge=40, le=200)
    buget: float = Field(..., description="Bugetul în EUR", ge=1000, le=500000)
    km_zi: float = Field(..., description="Km parcurși pe zi", ge=0, le=500)
    tip_combustibil: str = Field(..., description="benzina/diesel/electric/hybrid")


class BehavioralScores(BaseModel):
    """Scoruri agregate per axa. Range extins la 0-45 pentru a suporta v2 (15 intrebari)."""
    comfort: float = Field(default=0, ge=0, le=45)
    sport: float = Field(default=0, ge=0, le=45)
    siguranta: float = Field(default=0, ge=0, le=45)
    economie: float = Field(default=0, ge=0, le=45)
    estetica: float = Field(default=0, ge=0, le=45)


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
    recommendation_id: Optional[int] = None


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
    test_version_completed: Optional[int] = None
    is_complete: bool = False

    class Config:
        from_attributes = True


class UserProfileUpdate(BaseModel):
    inaltime: Optional[float] = Field(None, ge=140, le=220)
    greutate: Optional[float] = Field(None, ge=40, le=200)
    buget: Optional[float] = Field(None, ge=1000, le=500000)
    km_zi: Optional[float] = Field(None, ge=0, le=500)
    tip_combustibil: Optional[str] = None
    score_comfort: Optional[float] = Field(None, ge=0, le=45)
    score_sport: Optional[float] = Field(None, ge=0, le=45)
    score_siguranta: Optional[float] = Field(None, ge=0, le=45)
    score_economie: Optional[float] = Field(None, ge=0, le=45)
    score_estetica: Optional[float] = Field(None, ge=0, le=45)


class FeedbackCreate(BaseModel):
    car_id: int
    rating: int = Field(..., ge=-1, le=1)
    recommendation_id: Optional[int] = None
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
    car_id: int
    marca: str
    model: str
    likes: int
    dislikes: int
    neutral: int
    total: int
    score: float


class FeedbackStatsResponse(BaseModel):
    total_feedbacks: int
    most_liked: list[FeedbackStatsItem]
    most_disliked: list[FeedbackStatsItem]


# === Mini-test ===

class TestOptionResponse(BaseModel):
    id: int
    order_index: int
    text: str
    scores: dict

    class Config:
        from_attributes = True


class TestQuestionResponse(BaseModel):
    id: int
    order_index: int
    text: str
    options: list[TestOptionResponse]

    class Config:
        from_attributes = True


class TestQuestionsResponse(BaseModel):
    version: int
    total: int
    questions: list[TestQuestionResponse]


class TestAnswerInput(BaseModel):
    question_id: int
    option_id: int


class TestSubmitRequest(BaseModel):
    version: int = Field(..., description="Versiunea testului (ex: 1 sau 2)")
    answers: list[TestAnswerInput] = Field(..., min_length=1)


class TestSubmitResponse(BaseModel):
    submission_id: str
    version: int
    answered_count: int
    aggregated_scores: dict = Field(..., description="Suma scorurilor pe cele 5 axe")
    profile_updated: bool


class TestResponseHistoryItem(BaseModel):
    submission_id: str
    version: int
    answered_count: int
    aggregated_scores: dict
    submitted_at: datetime
