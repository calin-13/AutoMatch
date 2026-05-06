from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from jose import jwt
from models.schemas import (
    UserInput,
    RecommendationResponse,
    PhysiologicalData,
    BehavioralScores,
)
from models.database import Car, RecommendationHistory, UserProfile as UserProfileDB, User
from services.scoring import calculate_rule_based_scores
from services.recommender import get_recommendations
from services.auth_service import get_current_user, oauth2_scheme
from config import get_db, SECRET_KEY, ALGORITHM

router = APIRouter(prefix="/api", tags=["recommendations"])


def get_optional_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        sub = payload.get("sub")
        if sub:
            return db.query(User).filter(User.id == int(sub)).first()
    except Exception:
        pass
    return None


def _save_history(db, user_id, user_input, scores, recommendations):
    car_ids = ",".join([str(r.id) for r in recommendations])
    history = RecommendationHistory(
        user_id=user_id,
        inaltime=user_input.physiological.inaltime,
        greutate=user_input.physiological.greutate,
        buget=user_input.physiological.buget,
        km_zi=user_input.physiological.km_zi,
        tip_combustibil=user_input.physiological.tip_combustibil,
        score_comfort=scores.comfort,
        score_sport=scores.sport,
        score_siguranta=scores.siguranta,
        score_economie=scores.economie,
        score_estetica=scores.estetica,
        recommended_cars=car_ids,
    )
    db.add(history)
    db.commit()
    db.refresh(history)
    return history.id


@router.post("/recommend", response_model=RecommendationResponse)
def recommend_cars(user_input: UserInput, db: Session = Depends(get_db)):
    """Recomandare publica (fara auth, fara feedback re-ranking)."""
    try:
        scores = calculate_rule_based_scores(user_input)
        recommendations = get_recommendations(user_input, scores, db, user_id=None)
        return RecommendationResponse(
            recommendations=recommendations,
            user_profile=scores,
            recommendation_id=None,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/recommend-auth", response_model=RecommendationResponse)
def recommend_cars_auth(
    user_input: UserInput,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Recomandare cu autentificare. Aplica re-ranking pe baza feedback-ului anterior."""
    try:
        scores = calculate_rule_based_scores(user_input)
        recommendations = get_recommendations(
            user_input, scores, db, user_id=current_user.id
        )
        rec_id = _save_history(db, current_user.id, user_input, scores, recommendations)
        return RecommendationResponse(
            recommendations=recommendations,
            user_profile=scores,
            recommendation_id=rec_id,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/recommend-from-profile", response_model=RecommendationResponse)
def recommend_from_profile(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Recomandare din profil persistent. Aplica re-ranking pe baza feedback-ului."""
    profile_db = (
        db.query(UserProfileDB)
        .filter(UserProfileDB.user_id == current_user.id)
        .first()
    )
    if profile_db is None:
        raise HTTPException(
            status_code=404,
            detail="Profilul nu exista. Apeleaza GET /api/auth/profile pentru a-l crea.",
        )

    missing = []
    if profile_db.inaltime is None:
        missing.append("inaltime")
    if profile_db.greutate is None:
        missing.append("greutate")
    if profile_db.buget is None:
        missing.append("buget")
    if profile_db.km_zi is None:
        missing.append("km_zi")
    if profile_db.tip_combustibil is None:
        missing.append("tip_combustibil")
    if not profile_db.has_completed_test:
        missing.append("mini-test")

    if missing:
        raise HTTPException(
            status_code=400,
            detail=f"Profil incomplet. Lipsesc: {', '.join(missing)}",
        )

    user_input = UserInput(
        physiological=PhysiologicalData(
            inaltime=profile_db.inaltime,
            greutate=profile_db.greutate,
            buget=profile_db.buget,
            km_zi=profile_db.km_zi,
            tip_combustibil=profile_db.tip_combustibil,
        ),
        behavioral=BehavioralScores(
            comfort=profile_db.score_comfort or 0,
            sport=profile_db.score_sport or 0,
            siguranta=profile_db.score_siguranta or 0,
            economie=profile_db.score_economie or 0,
            estetica=profile_db.score_estetica or 0,
        ),
    )

    try:
        scores = calculate_rule_based_scores(user_input)
        recommendations = get_recommendations(
            user_input, scores, db, user_id=current_user.id
        )
        rec_id = _save_history(db, current_user.id, user_input, scores, recommendations)
        return RecommendationResponse(
            recommendations=recommendations,
            user_profile=scores,
            recommendation_id=rec_id,
        )
    except HTTPException:
        raise
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
        ],
    }


@router.get("/test-questions", deprecated=True, summary="DEPRECATED: foloseste GET /api/test/questions")
def get_test_questions_legacy(db: Session = Depends(get_db)):
    from api.test_routes import get_questions
    return get_questions(version=1, db=db)
