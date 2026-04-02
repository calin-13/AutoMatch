from sqlalchemy.orm import Session
from models.schemas import UserInput, UserProfile, CarRecommendation
from models.database import Car


def get_recommendations(
    user_input: UserInput, profile: UserProfile, db: Session, top_n: int = 5
) -> list[CarRecommendation]:
    candidates = _filter_cars(user_input, db)
    scored = _score_cars(candidates, profile)
    scored.sort(key=lambda x: x.score_total, reverse=True)
    return scored[:top_n]


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


def _score_cars(cars: list[Car], profile: UserProfile) -> list[CarRecommendation]:
    results = []

    for car in cars:
        score = (
            car.rating_comfort * (profile.comfort / 100) +
            car.rating_sport * (profile.sport / 100) +
            car.rating_siguranta * (profile.siguranta / 100) +
            car.rating_economie * (profile.economie / 100) +
            car.rating_estetica * (profile.estetica / 100)
        )

        max_possible = 5.0
        score_normalized = round((score / max_possible) * 100, 1)

        results.append(CarRecommendation(
            id=car.id,
            marca=car.marca,
            model=car.model,
            an=car.an,
            pret=car.pret,
            tip_combustibil=car.tip_combustibil,
            tip_caroserie=car.tip_caroserie,
            score_total=score_normalized,
            score_details={
                "comfort": round(car.rating_comfort * (profile.comfort / 100), 2),
                "sport": round(car.rating_sport * (profile.sport / 100), 2),
                "siguranta": round(car.rating_siguranta * (profile.siguranta / 100), 2),
                "economie": round(car.rating_economie * (profile.economie / 100), 2),
                "estetica": round(car.rating_estetica * (profile.estetica / 100), 2),
            }
        ))

    return results