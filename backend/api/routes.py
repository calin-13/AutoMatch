from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from models.schemas import UserInput, RecommendationResponse
from models.database import Car
from services.scoring import calculate_rule_based_scores
from services.recommender import get_recommendations
from config import get_db

router = APIRouter(prefix="/api", tags=["recommendations"])


@router.post("/recommend", response_model=RecommendationResponse)
def recommend_cars(user_input: UserInput, db: Session = Depends(get_db)):
    try:
        scores = calculate_rule_based_scores(user_input)
        recommendations = get_recommendations(user_input, scores, db)
        return RecommendationResponse(
            recommendations=recommendations,
            user_profile=scores
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cars")
def get_all_cars(db: Session = Depends(get_db)):
    cars = db.query(Car).all()
    return {
        "total": len(cars),
        "cars": [
            {
                "id": c.id,
                "marca": c.marca,
                "model": c.model,
                "an": c.an,
                "pret": c.pret,
                "tip_combustibil": c.tip_combustibil,
                "tip_caroserie": c.tip_caroserie,
                "putere_cp": c.putere_cp,
            }
            for c in cars
        ]
    }


@router.get("/test-questions")
def get_test_questions():
    questions = [
        {
            "id": 1,
            "text": "Cand conduci pe autostrada, ce este cel mai important pentru tine?",
            "options": [
                {"text": "Sa ma simt in siguranta", "scores": {"siguranta": 3, "comfort": 1}},
                {"text": "Sa simt puterea motorului", "scores": {"sport": 3, "estetica": 1}},
                {"text": "Sa consum cat mai putin", "scores": {"economie": 3, "comfort": 1}},
                {"text": "Sa am un drum lin si silentios", "scores": {"comfort": 3, "siguranta": 1}},
            ]
        },
        {
            "id": 2,
            "text": "Ce aspect al unei masini te atrage primul?",
            "options": [
                {"text": "Designul exterior", "scores": {"estetica": 3, "sport": 1}},
                {"text": "Spatiul interior", "scores": {"comfort": 3, "siguranta": 1}},
                {"text": "Consumul si costurile de intretinere", "scores": {"economie": 3, "siguranta": 1}},
                {"text": "Performantele tehnice", "scores": {"sport": 3, "estetica": 1}},
            ]
        },
        {
            "id": 3,
            "text": "Cum ai descrie stilul tau de condus?",
            "options": [
                {"text": "Prudent si atent", "scores": {"siguranta": 3, "economie": 1}},
                {"text": "Sportiv si dinamic", "scores": {"sport": 3, "estetica": 1}},
                {"text": "Relaxat si confortabil", "scores": {"comfort": 3, "economie": 1}},
                {"text": "Eficient si practic", "scores": {"economie": 3, "comfort": 1}},
            ]
        },
        {
            "id": 4,
            "text": "Daca ai avea buget nelimitat, ce masina ai alege?",
            "options": [
                {"text": "Un SUV mare si sigur (Volvo XC90)", "scores": {"siguranta": 3, "comfort": 2}},
                {"text": "Un supercar (Ferrari, Lamborghini)", "scores": {"sport": 3, "estetica": 2}},
                {"text": "O limuzina de lux (Mercedes S-Class)", "scores": {"comfort": 3, "estetica": 2}},
                {"text": "O masina electrica premium (Tesla)", "scores": {"economie": 2, "sport": 2, "estetica": 1}},
            ]
        },
        {
            "id": 5,
            "text": "Ce faci de obicei in weekend cu masina?",
            "options": [
                {"text": "Plimbari scurte prin oras", "scores": {"economie": 3, "comfort": 1}},
                {"text": "Drumuri lungi, excursii", "scores": {"comfort": 3, "siguranta": 1}},
                {"text": "Merg pe trasee montane/off-road", "scores": {"sport": 2, "siguranta": 2}},
                {"text": "O folosesc rar, prefer transportul public", "scores": {"economie": 3, "estetica": 1}},
            ]
        },
    ]
    return {"questions": questions}