from fastapi import APIRouter, HTTPException
from models.schemas import UserInput, RecommendationResponse
from services.scoring import calculate_rule_based_scores
from services.recommender import get_recommendations

router = APIRouter(prefix="/api", tags=["recommendations"])


@router.post("/recommend", response_model=RecommendationResponse)
def recommend_cars(user_input: UserInput):
    """
    Endpoint principal: primește datele utilizatorului și returnează recomandări auto.
    Pas 1: Scoring rule-based
    Pas 2: Rafinare cu model ML
    """
    try:
        # Pas 1: Calculează scorurile rule-based
        scores = calculate_rule_based_scores(user_input)

        # Pas 2: Obține recomandările finale (rule-based + ML)
        recommendations = get_recommendations(user_input, scores)

        return RecommendationResponse(
            recommendations=recommendations,
            user_profile=scores
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cars")
def get_all_cars():
    """Returnează lista tuturor mașinilor din baza de date."""
    # TODO: Implementare cu PostgreSQL
    return {"message": "Lista mașinilor - de implementat"}


@router.get("/test-questions")
def get_test_questions():
    """Returnează întrebările pentru mini-testul comportamental."""
    questions = [
        {
            "id": 1,
            "text": "Când conduci pe autostradă, ce este cel mai important pentru tine?",
            "options": [
                {"text": "Să mă simt în siguranță", "scores": {"siguranta": 3, "comfort": 1}},
                {"text": "Să simt puterea motorului", "scores": {"sport": 3, "estetica": 1}},
                {"text": "Să consum cât mai puțin", "scores": {"economie": 3, "comfort": 1}},
                {"text": "Să am un drum lin și silențios", "scores": {"comfort": 3, "siguranta": 1}},
            ]
        },
        {
            "id": 2,
            "text": "Ce aspect al unei mașini te atrage primul?",
            "options": [
                {"text": "Designul exterior", "scores": {"estetica": 3, "sport": 1}},
                {"text": "Spațiul interior", "scores": {"comfort": 3, "siguranta": 1}},
                {"text": "Consumul și costurile de întreținere", "scores": {"economie": 3, "siguranta": 1}},
                {"text": "Performanțele tehnice", "scores": {"sport": 3, "estetica": 1}},
            ]
        },
        {
            "id": 3,
            "text": "Cum ai descrie stilul tău de condus?",
            "options": [
                {"text": "Prudent și atent", "scores": {"siguranta": 3, "economie": 1}},
                {"text": "Sportiv și dinamic", "scores": {"sport": 3, "estetica": 1}},
                {"text": "Relaxat și confortabil", "scores": {"comfort": 3, "economie": 1}},
                {"text": "Eficient și practic", "scores": {"economie": 3, "comfort": 1}},
            ]
        },
        {
            "id": 4,
            "text": "Dacă ai avea buget nelimitat, ce mașină ai alege?",
            "options": [
                {"text": "Un SUV mare și sigur (Volvo XC90)", "scores": {"siguranta": 3, "comfort": 2}},
                {"text": "Un supercar (Ferrari, Lamborghini)", "scores": {"sport": 3, "estetica": 2}},
                {"text": "O limuzină de lux (Mercedes S-Class)", "scores": {"comfort": 3, "estetica": 2}},
                {"text": "O mașină electrică premium (Tesla)", "scores": {"economie": 2, "sport": 2, "estetica": 1}},
            ]
        },
        {
            "id": 5,
            "text": "Ce faci de obicei în weekend cu mașina?",
            "options": [
                {"text": "Plimbări scurte prin oraș", "scores": {"economie": 3, "comfort": 1}},
                {"text": "Drumuri lungi, excursii", "scores": {"comfort": 3, "siguranta": 1}},
                {"text": "Merg pe trasee montane/off-road", "scores": {"sport": 2, "siguranta": 2}},
                {"text": "O folosesc rar, prefer transportul public", "scores": {"economie": 3, "estetica": 1}},
            ]
        },
    ]
    return {"questions": questions}
