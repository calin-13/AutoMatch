from pydantic import BaseModel, Field
from typing import Optional


class PhysiologicalData(BaseModel):
    """Date fiziologice și practice ale utilizatorului."""
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
    """Input complet de la utilizator."""
    physiological: PhysiologicalData
    behavioral: BehavioralScores


class CarRecommendation(BaseModel):
    """O recomandare de mașină."""
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
    """Profilul generat al utilizatorului."""
    comfort: float
    sport: float
    siguranta: float
    economie: float
    estetica: float
    categorie_buget: str
    categorie_utilizare: str


class RecommendationResponse(BaseModel):
    """Răspunsul complet cu recomandări."""
    recommendations: list[CarRecommendation]
    user_profile: UserProfile
