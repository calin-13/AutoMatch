from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from models.database import RecommendationFeedback, Car


# Greutati pentru atribute similare (suma maxima posibila per perechi feedback)
WEIGHT_BRAND = 0.5
WEIGHT_BODYTYPE = 0.4
WEIGHT_FUEL = 0.3
WEIGHT_PRICE_SEGMENT = 0.2

# Toleranta pentru segmentul de pret (mașini "asemănătoare" ca pret)
PRICE_TOLERANCE = 0.20

# Numar de feedback-uri peste care factorul de incredere e maxim
CONFIDENCE_THRESHOLD = 5

# Adjustare maxima posibila per masina (clamp la +/- aceasta valoare)
MAX_ADJUSTMENT = 8.0


def get_user_feedback_with_cars(db: Session, user_id: int) -> list:
    """Returneaza toate feedback-urile user-ului impreuna cu detalii masina."""
    rows = (
        db.query(RecommendationFeedback, Car)
        .join(Car, Car.id == RecommendationFeedback.car_id)
        .filter(RecommendationFeedback.user_id == user_id)
        .all()
    )
    return [(fb, car) for fb, car in rows]


def compute_feedback_adjustment(
    candidate_car: Car, user_feedbacks: list
) -> dict:
    """
    Calculeaza ajustarea de scor pentru o masina candidata pe baza feedback-urilor anterioare ale user-ului.
    Returneaza un dict cu detalii (pentru afisare in frontend).
    """
    if not user_feedbacks:
        return {"adjustment": 0.0, "matches": [], "confidence": 0.0}

    raw_score = 0.0
    matches = []

    for fb, fb_car in user_feedbacks:
        # Skip feedback pe aceeasi masina (nu compari masina cu ea insasi)
        if fb_car.id == candidate_car.id:
            continue

        rating = fb.rating  # -1, 0, +1
        if rating == 0:
            continue  # neutral nu influenteaza

        contribution = 0.0
        match_reasons = []

        if fb_car.marca == candidate_car.marca:
            contribution += WEIGHT_BRAND * rating
            match_reasons.append(f"marca {candidate_car.marca}")

        if fb_car.tip_caroserie == candidate_car.tip_caroserie:
            contribution += WEIGHT_BODYTYPE * rating
            match_reasons.append(f"caroserie {candidate_car.tip_caroserie}")

        if fb_car.tip_combustibil == candidate_car.tip_combustibil:
            contribution += WEIGHT_FUEL * rating
            match_reasons.append(f"combustibil {candidate_car.tip_combustibil}")

        # Segment pret (in raza de PRICE_TOLERANCE)
        if fb_car.pret > 0 and candidate_car.pret > 0:
            ratio = abs(fb_car.pret - candidate_car.pret) / fb_car.pret
            if ratio <= PRICE_TOLERANCE:
                contribution += WEIGHT_PRICE_SEGMENT * rating
                match_reasons.append("segment pret similar")

        if contribution != 0.0 and match_reasons:
            raw_score += contribution
            matches.append({
                "feedback_car_id": fb_car.id,
                "feedback_car_label": f"{fb_car.marca} {fb_car.model}",
                "rating": rating,
                "shared_attributes": match_reasons,
                "contribution": round(contribution, 3),
            })

    # Factor de incredere: creste cu numarul de feedback-uri non-neutrale
    non_neutral_count = sum(1 for fb, _ in user_feedbacks if fb.rating != 0)
    confidence = min(non_neutral_count / CONFIDENCE_THRESHOLD, 1.0)

    adjustment = raw_score * confidence

    # Clamp la +/- MAX_ADJUSTMENT
    adjustment = max(-MAX_ADJUSTMENT, min(MAX_ADJUSTMENT, adjustment))

    return {
        "adjustment": round(adjustment, 2),
        "matches": matches,
        "confidence": round(confidence, 2),
        "raw_score": round(raw_score, 3),
    }


def aggregate_feedback_by_attribute(db: Session, user_id: int) -> dict:
    """
    Agregheaza feedback-ul user-ului pe atribute (marca, caroserie, combustibil).
    Util pentru endpoint-ul de summary si pentru afisare frontend.
    """
    feedbacks = get_user_feedback_with_cars(db, user_id)

    by_brand = {}
    by_bodytype = {}
    by_fuel = {}

    for fb, car in feedbacks:
        if fb.rating == 0:
            continue

        # Marca
        b = by_brand.setdefault(car.marca, {"likes": 0, "dislikes": 0})
        if fb.rating == 1:
            b["likes"] += 1
        else:
            b["dislikes"] += 1

        # Caroserie
        c = by_bodytype.setdefault(car.tip_caroserie, {"likes": 0, "dislikes": 0})
        if fb.rating == 1:
            c["likes"] += 1
        else:
            c["dislikes"] += 1

        # Combustibil
        f = by_fuel.setdefault(car.tip_combustibil, {"likes": 0, "dislikes": 0})
        if fb.rating == 1:
            f["likes"] += 1
        else:
            f["dislikes"] += 1

    def _to_list(d):
        return [
            {"key": k, "likes": v["likes"], "dislikes": v["dislikes"], "net": v["likes"] - v["dislikes"]}
            for k, v in d.items()
        ]

    total = sum(1 for fb, _ in feedbacks if fb.rating != 0)

    return {
        "total_feedbacks": total,
        "by_brand": sorted(_to_list(by_brand), key=lambda x: -x["net"]),
        "by_bodytype": sorted(_to_list(by_bodytype), key=lambda x: -x["net"]),
        "by_fuel": sorted(_to_list(by_fuel), key=lambda x: -x["net"]),
    }
