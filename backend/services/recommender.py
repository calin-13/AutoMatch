from sqlalchemy.orm import Session
from typing import Optional
from models.schemas import UserInput, UserProfile, CarRecommendation
from models.database import Car
from services.ml_service import (
    is_available as ml_available,
    predict_score as ml_predict,
    explain_prediction as ml_explain,
)
from services.feedback_service import (
    get_user_feedback_with_cars,
    compute_feedback_adjustment,
)


# MMR config
MMR_LAMBDA = 0.7
DIVERSITY_PENALTY_BRAND = 1.0
DIVERSITY_PENALTY_BODYTYPE = 0.6
DIVERSITY_PENALTY_FUEL = 0.3


def get_recommendations(
    user_input: UserInput,
    profile: UserProfile,
    db: Session,
    top_n: int = 5,
    user_id: Optional[int] = None,
    use_diversity: bool = False,
) -> list[CarRecommendation]:
    """
    Pipeline:
    1. Filtrare candidate
    2. Scoring ML / rule-based
    3. Re-ranking pe baza feedback-ului (autentificat)
    4. Diversitate MMR (opțional)
    5. Top N cu SHAP
    """
    candidates = _filter_cars(user_input, db)
    cars_by_id = {c.id: c for c in candidates}

    if ml_available():
        scored = _score_cars_ml(candidates, profile, user_input)
    else:
        scored = _score_cars_rule_based(candidates, profile)

    if user_id is not None:
        feedbacks = get_user_feedback_with_cars(db, user_id)
        if feedbacks:
            scored = _apply_feedback_reranking(scored, cars_by_id, feedbacks)

    scored.sort(key=lambda x: x.score_total, reverse=True)

    # Selectie finala: MMR sau simpla
    if use_diversity and len(scored) > top_n:
        top = _apply_mmr_diversity(scored, cars_by_id, top_n)
    else:
        top = scored[:top_n]

    if ml_available():
        budget = user_input.physiological.buget
        km_zi = user_input.physiological.km_zi
        for rec in top:
            car = cars_by_id.get(rec.id)
            if car is None:
                continue
            explanation = ml_explain(profile, car, budget, km_zi, top_n=5)
            if explanation:
                rec.score_details["explanation"] = explanation

    return top


def _filter_cars(user_input: UserInput, db: Session) -> list[Car]:
    budget = user_input.physiological.buget
    fuel_pref = user_input.physiological.tip_combustibil

    query = db.query(Car).filter(Car.pret <= budget * 1.1)

    if fuel_pref and fuel_pref != "orice":
        filtered = query.filter(Car.tip_combustibil == fuel_pref).all()
        if not filtered:
            filtered = db.query(Car).filter(Car.pret <= budget * 1.1).all()
        return filtered

    return query.all()


def _apply_feedback_reranking(
    recommendations: list[CarRecommendation],
    cars_by_id: dict,
    user_feedbacks: list,
) -> list[CarRecommendation]:
    for rec in recommendations:
        car = cars_by_id.get(rec.id)
        if car is None:
            continue

        adj_result = compute_feedback_adjustment(car, user_feedbacks)
        adjustment = adj_result["adjustment"]

        rec.score_details["feedback_adjustment"] = adj_result
        new_score = rec.score_total + adjustment
        rec.score_total = round(max(0.0, min(100.0, new_score)), 1)

    return recommendations


def _apply_mmr_diversity(
    sorted_recs: list[CarRecommendation],
    cars_by_id: dict,
    top_n: int,
) -> list[CarRecommendation]:
    """
    Maximal Marginal Relevance: la fiecare pas alegem masina care maximizeaza
    lambda * relevanta - (1-lambda) * similaritate_max_cu_selectate
    """
    if not sorted_recs:
        return []

    # Normalizez scorurile la 0-1 pentru a combina cu penalitati
    max_score = max(r.score_total for r in sorted_recs) or 1.0
    candidates = list(sorted_recs)
    selected = [candidates.pop(0)]

    while len(selected) < top_n and candidates:
        best_idx = 0
        best_mmr = -float("inf")

        for i, cand in enumerate(candidates):
            cand_car = cars_by_id.get(cand.id)
            if cand_car is None:
                continue

            relevance = cand.score_total / max_score

            # Calculez similaritatea maxima fata de orice mașină deja selectată
            max_similarity = 0.0
            for sel in selected:
                sel_car = cars_by_id.get(sel.id)
                if sel_car is None:
                    continue
                sim = _similarity(cand_car, sel_car)
                if sim > max_similarity:
                    max_similarity = sim

            mmr = MMR_LAMBDA * relevance - (1 - MMR_LAMBDA) * max_similarity

            if mmr > best_mmr:
                best_mmr = mmr
                best_idx = i

        chosen = candidates.pop(best_idx)
        chosen_car = cars_by_id.get(chosen.id)
        # Notez diversitatea aplicata (audit pentru frontend)
        chosen.score_details["diversity_applied"] = True
        selected.append(chosen)

    for s in selected:
        s.score_details.setdefault("diversity_applied", True)
    return selected


def _similarity(car_a: Car, car_b: Car) -> float:
    """Similaritate intre 0 si 1 pe baza atributelor partajate."""
    sim = 0.0
    total_weight = (
        DIVERSITY_PENALTY_BRAND + DIVERSITY_PENALTY_BODYTYPE + DIVERSITY_PENALTY_FUEL
    )

    if car_a.marca == car_b.marca:
        sim += DIVERSITY_PENALTY_BRAND
    if car_a.tip_caroserie == car_b.tip_caroserie:
        sim += DIVERSITY_PENALTY_BODYTYPE
    if car_a.tip_combustibil == car_b.tip_combustibil:
        sim += DIVERSITY_PENALTY_FUEL

    return sim / total_weight if total_weight > 0 else 0.0


def _score_cars_ml(
    cars: list[Car], profile: UserProfile, user_input: UserInput
) -> list[CarRecommendation]:
    results = []
    budget = user_input.physiological.buget
    km_zi = user_input.physiological.km_zi

    for car in cars:
        prediction = ml_predict(profile, car, budget, km_zi)

        if prediction:
            score = prediction["score"]
            method = "ml"
        else:
            score = _calculate_rule_based_score(car, profile)
            method = "rule_based"

        rb_score = _calculate_rule_based_score(car, profile)

        results.append(CarRecommendation(
            id=car.id,
            marca=car.marca,
            model=car.model,
            an=car.an,
            pret=car.pret,
            tip_combustibil=car.tip_combustibil,
            tip_caroserie=car.tip_caroserie,
            score_total=score,
            score_details={
                "comfort": round(car.rating_comfort * (profile.comfort / 100), 2),
                "sport": round(car.rating_sport * (profile.sport / 100), 2),
                "siguranta": round(car.rating_siguranta * (profile.siguranta / 100), 2),
                "economie": round(car.rating_economie * (profile.economie / 100), 2),
                "estetica": round(car.rating_estetica * (profile.estetica / 100), 2),
                "scoring_method": method,
                "rule_based_score": rb_score,
                "ml_score_before_feedback": score,
            }
        ))

    return results


def _score_cars_rule_based(
    cars: list[Car], profile: UserProfile
) -> list[CarRecommendation]:
    results = []
    for car in cars:
        score = _calculate_rule_based_score(car, profile)
        results.append(CarRecommendation(
            id=car.id,
            marca=car.marca,
            model=car.model,
            an=car.an,
            pret=car.pret,
            tip_combustibil=car.tip_combustibil,
            tip_caroserie=car.tip_caroserie,
            score_total=score,
            score_details={
                "comfort": round(car.rating_comfort * (profile.comfort / 100), 2),
                "sport": round(car.rating_sport * (profile.sport / 100), 2),
                "siguranta": round(car.rating_siguranta * (profile.siguranta / 100), 2),
                "economie": round(car.rating_economie * (profile.economie / 100), 2),
                "estetica": round(car.rating_estetica * (profile.estetica / 100), 2),
                "scoring_method": "rule_based",
                "rule_based_score": score,
                "ml_score_before_feedback": None,
            }
        ))
    return results


def _calculate_rule_based_score(car: Car, profile: UserProfile) -> float:
    score = (
        car.rating_comfort * (profile.comfort / 100) +
        car.rating_sport * (profile.sport / 100) +
        car.rating_siguranta * (profile.siguranta / 100) +
        car.rating_economie * (profile.economie / 100) +
        car.rating_estetica * (profile.estetica / 100)
    )
    return round((score / 5.0) * 100, 1)
