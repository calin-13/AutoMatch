from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct
from jose import jwt
from typing import Optional
from models.schemas import (
    UserInput,
    RecommendationResponse,
    PhysiologicalData,
    BehavioralScores,
    CarDetailResponse,
    CarSearchResponse,
    StatsResponse,
    StatsDistributionItem,
    SessionFeedbackCreate,
    SessionFeedbackResponse,
)
from models.database import (
    Car, RecommendationHistory, Recommendation, RecommendationItem,
    UserProfile as UserProfileDB, User
)
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


def _save_history(
    db, user_id, user_input, scores, recommendations,
    scoring_method: str = "ml", has_feedback_reranking: bool = False,
    total_candidates: Optional[int] = None,
):
    """
    Salveaza in AMBELE tabele:
    - recommendation_history (LEGACY, CSV) pentru compat
    - recommendations + recommendation_items (NORMALIZED) pentru viitor
    Returneaza id-ul din legacy (pentru compat cu feedback existent).
    """
    car_ids = ",".join([str(r.id) for r in recommendations])

    legacy = RecommendationHistory(
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
    db.add(legacy)
    db.flush()

    profile_snapshot = {
        "physiological": user_input.physiological.model_dump(),
        "behavioral": user_input.behavioral.model_dump(),
        "derived_profile": scores.model_dump(),
    }

    rec = Recommendation(
        user_id=user_id,
        profile_snapshot=profile_snapshot,
        scoring_method=scoring_method,
        has_feedback_reranking=has_feedback_reranking,
        total_candidates=total_candidates,
    )
    db.add(rec)
    db.flush()

    for idx, r in enumerate(recommendations, start=1):
        item = RecommendationItem(
            recommendation_id=rec.id,
            car_id=r.id,
            rank=idx,
            score_total=r.score_total,
            score_details=r.score_details,
        )
        db.add(item)

    db.commit()
    db.refresh(legacy)
    db.refresh(rec)
    return {"legacy_id": legacy.id, "session_id": rec.id}


def _detect_scoring_method(recommendations) -> str:
    if not recommendations:
        return "ml"
    sd = recommendations[0].score_details
    return sd.get("scoring_method", "ml")


def _has_feedback_reranking(recommendations) -> bool:
    if not recommendations:
        return False
    sd = recommendations[0].score_details
    fb = sd.get("feedback_adjustment")
    return fb is not None and fb.get("matches", []) != []


@router.post("/recommend", response_model=RecommendationResponse)
def recommend_cars(user_input: UserInput, db: Session = Depends(get_db)):
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
    diversity: bool = False,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        scores = calculate_rule_based_scores(user_input)
        recommendations = get_recommendations(
            user_input, scores, db, user_id=current_user.id, use_diversity=diversity
        )
        ids = _save_history(
            db, current_user.id, user_input, scores, recommendations,
            scoring_method=_detect_scoring_method(recommendations),
            has_feedback_reranking=_has_feedback_reranking(recommendations),
        )
        return RecommendationResponse(
            recommendations=recommendations,
            user_profile=scores,
            recommendation_id=ids["legacy_id"],
            session_id=ids["session_id"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/recommend-from-profile", response_model=RecommendationResponse)
def recommend_from_profile(
    diversity: bool = False,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
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
        # Calculez total masini si pool-ul de candidati (pentru transparenta in UI)
        total_in_db = db.query(func.count(Car.id)).scalar() or 0
        budget_cap = user_input.physiological.buget * 1.1
        fuel_pref = user_input.physiological.tip_combustibil
        if fuel_pref and fuel_pref != "orice":
            total_candidates = db.query(func.count(Car.id)).filter(
                Car.pret <= budget_cap, Car.tip_combustibil == fuel_pref
            ).scalar() or 0
            if total_candidates == 0:
                total_candidates = db.query(func.count(Car.id)).filter(Car.pret <= budget_cap).scalar() or 0
        else:
            total_candidates = db.query(func.count(Car.id)).filter(Car.pret <= budget_cap).scalar() or 0

        scores = calculate_rule_based_scores(user_input)
        recommendations = get_recommendations(
            user_input, scores, db, user_id=current_user.id, use_diversity=diversity
        )
        ids = _save_history(
            db, current_user.id, user_input, scores, recommendations,
            scoring_method=_detect_scoring_method(recommendations),
            has_feedback_reranking=_has_feedback_reranking(recommendations),
            total_candidates=total_candidates,
        )
        return RecommendationResponse(
            recommendations=recommendations,
            user_profile=scores,
            recommendation_id=ids["legacy_id"],
            session_id=ids["session_id"],
            total_candidates=total_candidates,
            total_in_db=total_in_db,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# === Catalog masini ===

@router.get("/cars")
def get_all_cars(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    total = db.query(func.count(Car.id)).scalar()
    cars = (
        db.query(Car)
        .order_by(Car.id)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
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


@router.get("/cars/search", response_model=CarSearchResponse)
def search_cars(
    marca: Optional[str] = None,
    tip_combustibil: Optional[str] = None,
    tip_caroserie: Optional[str] = None,
    pret_min: Optional[float] = None,
    pret_max: Optional[float] = None,
    putere_min: Optional[int] = None,
    putere_max: Optional[int] = None,
    an_min: Optional[int] = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    q = db.query(Car)

    if marca:
        q = q.filter(Car.marca.ilike(f"%{marca}%"))
    if tip_combustibil:
        q = q.filter(Car.tip_combustibil == tip_combustibil)
    if tip_caroserie:
        q = q.filter(Car.tip_caroserie == tip_caroserie)
    if pret_min is not None:
        q = q.filter(Car.pret >= pret_min)
    if pret_max is not None:
        q = q.filter(Car.pret <= pret_max)
    if putere_min is not None:
        q = q.filter(Car.putere_cp >= putere_min)
    if putere_max is not None:
        q = q.filter(Car.putere_cp <= putere_max)
    if an_min is not None:
        q = q.filter(Car.an >= an_min)

    total = q.count()
    cars = q.order_by(Car.pret).offset((page - 1) * page_size).limit(page_size).all()

    return CarSearchResponse(
        total=total,
        page=page,
        page_size=page_size,
        cars=[CarDetailResponse.model_validate(c) for c in cars],
    )


@router.get("/cars/{car_id}", response_model=CarDetailResponse)
def get_car_by_id(car_id: int, db: Session = Depends(get_db)):
    car = db.query(Car).filter(Car.id == car_id).first()
    if car is None:
        raise HTTPException(status_code=404, detail=f"Masina cu id={car_id} nu exista")
    return CarDetailResponse.model_validate(car)


@router.get("/stats", response_model=StatsResponse)
def get_stats(db: Session = Depends(get_db)):
    total = db.query(func.count(Car.id)).scalar() or 0

    by_brand_rows = (
        db.query(Car.marca, func.count(Car.id))
        .group_by(Car.marca)
        .order_by(func.count(Car.id).desc())
        .all()
    )
    by_fuel_rows = (
        db.query(Car.tip_combustibil, func.count(Car.id))
        .group_by(Car.tip_combustibil)
        .order_by(func.count(Car.id).desc())
        .all()
    )
    by_bodytype_rows = (
        db.query(Car.tip_caroserie, func.count(Car.id))
        .group_by(Car.tip_caroserie)
        .order_by(func.count(Car.id).desc())
        .all()
    )

    # Segmente preț
    segments = [
        ("economic", 0, 10000),
        ("mediu", 10000, 25000),
        ("premium", 25000, 60000),
        ("lux", 60000, 1_000_000),
    ]
    by_price_rows = []
    for label, lo, hi in segments:
        count = (
            db.query(func.count(Car.id))
            .filter(Car.pret >= lo, Car.pret < hi)
            .scalar()
        )
        by_price_rows.append((label, count or 0))

    avg_pret = db.query(func.avg(Car.pret)).scalar() or 0.0
    avg_putere = db.query(func.avg(Car.putere_cp)).scalar() or 0.0
    avg_consum = db.query(func.avg(Car.consum_mediu)).scalar() or 0.0

    return StatsResponse(
        total_cars=total,
        by_brand=[StatsDistributionItem(key=str(k), count=int(v)) for k, v in by_brand_rows],
        by_fuel=[StatsDistributionItem(key=str(k), count=int(v)) for k, v in by_fuel_rows],
        by_bodytype=[StatsDistributionItem(key=str(k), count=int(v)) for k, v in by_bodytype_rows],
        by_price_segment=[StatsDistributionItem(key=k, count=v) for k, v in by_price_rows],
        avg_pret=round(float(avg_pret), 2),
        avg_putere_cp=round(float(avg_putere), 2),
        avg_consum=round(float(avg_consum), 2),
    )


@router.post(
    "/recommendations/{rec_id}/feedback",
    response_model=SessionFeedbackResponse,
    summary="Trimite evaluarea finala (rating 1-5 + comentariu) pentru o sesiune de recomandare",
)
def submit_session_feedback(
    rec_id: int,
    payload: SessionFeedbackCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    rec = (
        db.query(Recommendation)
        .filter(Recommendation.id == rec_id, Recommendation.user_id == current_user.id)
        .first()
    )
    if rec is None:
        raise HTTPException(
            status_code=404,
            detail=f"Recomandarea {rec_id} nu exista sau nu apartine acestui utilizator",
        )
    rec.session_rating = payload.rating
    rec.session_comment = payload.comment
    db.commit()
    db.refresh(rec)
    return SessionFeedbackResponse(
        id=rec.id,
        rating=rec.session_rating,
        comment=rec.session_comment,
    )


@router.get("/test-questions", deprecated=True, summary="DEPRECATED: foloseste GET /api/test/questions")
def get_test_questions_legacy(db: Session = Depends(get_db)):
    from api.test_routes import get_questions
    return get_questions(version=1, db=db)
