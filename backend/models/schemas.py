from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class PhysiologicalData(BaseModel):
    inaltime: float = Field(..., ge=140, le=220)
    greutate: float = Field(..., ge=40, le=200)
    buget: float = Field(..., ge=1000, le=500000)
    km_zi: float = Field(..., ge=0, le=500)
    tip_combustibil: str


class BehavioralScores(BaseModel):
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
    score_total: float
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
    session_id: Optional[int] = None
    total_candidates: Optional[int] = None
    total_in_db: Optional[int] = None


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
    version: int
    answers: list[TestAnswerInput] = Field(..., min_length=1)


class TestSubmitResponse(BaseModel):
    submission_id: str
    version: int
    answered_count: int
    aggregated_scores: dict
    profile_updated: bool


class TestAnswerItem(BaseModel):
    question_id: int
    option_id: int


class TestResponseHistoryItem(BaseModel):
    submission_id: str
    version: int
    answered_count: int
    aggregated_scores: dict
    answers: list[TestAnswerItem] = []
    submitted_at: datetime


class SessionFeedbackCreate(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = Field(default=None, max_length=1000)


class SessionFeedbackResponse(BaseModel):
    id: int
    rating: int
    comment: Optional[str] = None


# === NOI: detalii masina, search, stats ===

class CarDetailResponse(BaseModel):
    id: int
    marca: str
    model: str
    an: int
    pret: float
    tip_combustibil: str
    tip_caroserie: str
    putere_cp: Optional[int] = None
    consum_mediu: Optional[float] = None
    emisii_co2: Optional[float] = None
    lungime_mm: Optional[int] = None
    latime_mm: Optional[int] = None
    inaltime_mm: Optional[int] = None
    volum_portbagaj: Optional[int] = None
    numar_locuri: Optional[int] = None
    rating_siguranta: Optional[float] = None
    rating_comfort: Optional[float] = None
    rating_sport: Optional[float] = None
    rating_economie: Optional[float] = None
    rating_estetica: Optional[float] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CarSearchResponse(BaseModel):
    total: int
    page: int
    page_size: int
    cars: list[CarDetailResponse]


class StatsDistributionItem(BaseModel):
    key: str
    count: int


class StatsResponse(BaseModel):
    total_cars: int
    by_brand: list[StatsDistributionItem]
    by_fuel: list[StatsDistributionItem]
    by_bodytype: list[StatsDistributionItem]
    by_price_segment: list[StatsDistributionItem]
    avg_pret: float
    avg_putere_cp: float
    avg_consum: float


# === NOI: recomandari normalizate (replace history) ===

class RecommendationItemDetail(BaseModel):
    rank: int
    car_id: int
    marca: str
    model: str
    an: int
    pret: float
    tip_combustibil: str
    tip_caroserie: str
    score_total: float
    score_details: dict = Field(default_factory=dict)


class RecommendationDetailResponse(BaseModel):
    id: int
    user_id: int
    profile_snapshot: dict
    scoring_method: str
    has_feedback_reranking: bool
    total_candidates: Optional[int] = None
    created_at: datetime
    items: list[RecommendationItemDetail]


class RecommendationListItem(BaseModel):
    id: int
    scoring_method: str
    has_feedback_reranking: bool
    items_count: int
    top_car_marca: Optional[str] = None
    top_car_model: Optional[str] = None
    top_score: Optional[float] = None
    created_at: datetime


class RecommendationListResponse(BaseModel):
    total: int
    recommendations: list[RecommendationListItem]


class AdminUserItem(BaseModel):
    id: int
    email: str
    username: str
    role: str
    has_profile: bool
    profile_complete: bool
    recommendations_count: int
    feedbacks_count: int
    created_at: datetime


class AdminUsersResponse(BaseModel):
    total: int
    users: list[AdminUserItem]


class AdminPlatformStats(BaseModel):
    total_users: int
    total_admins: int
    total_recommendations: int
    total_feedbacks: int
    feedbacks_positive: int
    feedbacks_negative: int
    feedbacks_neutral: int
    most_recommended_cars: list[dict]
    most_active_users: list[dict]


class AdminMLMetrics(BaseModel):
    has_metrics: bool
    regressor: Optional[dict] = None
    classifier: Optional[dict] = None
    comparison: Optional[dict] = None
    feature_importance: Optional[dict] = None


class AdminRecentFeedbackItem(BaseModel):
    id: int
    user_id: int
    username: str
    car_id: int
    car_marca: str
    car_model: str
    rating: int
    comment: Optional[str] = None
    created_at: datetime


class PromoteRequest(BaseModel):
    user_id: int

