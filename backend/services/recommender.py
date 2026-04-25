from sqlalchemy.orm import Session
from models.schemas import UserInput, UserProfile, CarRecommendation
from models.database import Car
from services.ml_service import (
    is_available as ml_available,
    predict_score as ml_predict,
    explain_prediction as ml_explain,
)


def get_recommendations(
    user_input: UserInput, profile: UserProfile, db: Session, top_n: int = 5
) -> list[CarRecommendation]:
    candidates = _filter_cars(user_input, db)
    cars_by_id = {c.id: c for c in candidates}

    if ml_available():
        scored = _score_cars_ml(candidates, profile, user_input)
    else:
        scored = _score_cars_rule_based(candidates, profile)

    scored.sort(key=lambda x: x.score_total, reverse=True)
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
