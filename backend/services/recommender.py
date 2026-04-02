from models.schemas import UserInput, UserProfile, CarRecommendation
import json
import os

# Date temporare până la integrarea cu PostgreSQL
SAMPLE_CARS = [
    {
        "id": 1, "marca": "Dacia", "model": "Logan", "an": 2023,
        "pret": 9500, "tip_combustibil": "benzina", "tip_caroserie": "sedan",
        "ratings": {"comfort": 3.0, "sport": 1.5, "siguranta": 3.5, "economie": 4.8, "estetica": 2.5}
    },
    {
        "id": 2, "marca": "Volkswagen", "model": "Golf 8", "an": 2023,
        "pret": 25000, "tip_combustibil": "benzina", "tip_caroserie": "hatchback",
        "ratings": {"comfort": 4.0, "sport": 3.5, "siguranta": 4.5, "economie": 3.5, "estetica": 4.0}
    },
    {
        "id": 3, "marca": "BMW", "model": "Seria 3", "an": 2023,
        "pret": 38000, "tip_combustibil": "diesel", "tip_caroserie": "sedan",
        "ratings": {"comfort": 4.5, "sport": 4.5, "siguranta": 4.5, "economie": 3.0, "estetica": 4.8}
    },
    {
        "id": 4, "marca": "Toyota", "model": "Corolla", "an": 2023,
        "pret": 22000, "tip_combustibil": "hybrid", "tip_caroserie": "sedan",
        "ratings": {"comfort": 4.0, "sport": 2.5, "siguranta": 4.8, "economie": 4.5, "estetica": 3.5}
    },
    {
        "id": 5, "marca": "Tesla", "model": "Model 3", "an": 2023,
        "pret": 42000, "tip_combustibil": "electric", "tip_caroserie": "sedan",
        "ratings": {"comfort": 4.2, "sport": 4.5, "siguranta": 4.8, "economie": 4.0, "estetica": 4.5}
    },
    {
        "id": 6, "marca": "Skoda", "model": "Octavia", "an": 2023,
        "pret": 23000, "tip_combustibil": "diesel", "tip_caroserie": "break",
        "ratings": {"comfort": 4.2, "sport": 2.5, "siguranta": 4.2, "economie": 4.2, "estetica": 3.5}
    },
    {
        "id": 7, "marca": "Mazda", "model": "CX-5", "an": 2023,
        "pret": 32000, "tip_combustibil": "benzina", "tip_caroserie": "suv",
        "ratings": {"comfort": 4.3, "sport": 3.5, "siguranta": 4.5, "economie": 3.0, "estetica": 4.5}
    },
    {
        "id": 8, "marca": "Hyundai", "model": "Tucson", "an": 2023,
        "pret": 28000, "tip_combustibil": "hybrid", "tip_caroserie": "suv",
        "ratings": {"comfort": 4.0, "sport": 3.0, "siguranta": 4.5, "economie": 4.0, "estetica": 4.2}
    },
    {
        "id": 9, "marca": "Ford", "model": "Puma", "an": 2023,
        "pret": 21000, "tip_combustibil": "hybrid", "tip_caroserie": "suv",
        "ratings": {"comfort": 3.8, "sport": 3.5, "siguranta": 4.0, "economie": 4.0, "estetica": 4.0}
    },
    {
        "id": 10, "marca": "Dacia", "model": "Duster", "an": 2023,
        "pret": 18000, "tip_combustibil": "benzina", "tip_caroserie": "suv",
        "ratings": {"comfort": 3.2, "sport": 2.5, "siguranta": 3.5, "economie": 4.5, "estetica": 3.5}
    },
]


def get_recommendations(
    user_input: UserInput, profile: UserProfile, top_n: int = 5
) -> list[CarRecommendation]:
    """
    Generează recomandări pe baza profilului utilizatorului.
    Pas 1: Filtrare pe buget și combustibil
    Pas 2: Scoring rule-based
    Pas 3 (TODO): Rafinare cu ML
    """
    candidates = _filter_cars(user_input)
    scored = _score_cars(candidates, profile)

    # Sortare descrescător după scor și returnare top N
    scored.sort(key=lambda x: x.score_total, reverse=True)
    return scored[:top_n]


def _filter_cars(user_input: UserInput) -> list[dict]:
    """Filtrează mașinile pe baza bugetului și preferinței de combustibil."""
    budget = user_input.physiological.buget
    fuel_pref = user_input.physiological.tip_combustibil

    filtered = []
    for car in SAMPLE_CARS:
        # Permite un buget cu 10% peste limită
        if car["pret"] > budget * 1.1:
            continue

        # Dacă utilizatorul are preferință de combustibil, filtrăm
        if fuel_pref and fuel_pref != "orice":
            if car["tip_combustibil"] != fuel_pref:
                continue

        filtered.append(car)

    # Dacă nu avem rezultate cu filtrul strict, relaxăm filtrul de combustibil
    if not filtered:
        filtered = [c for c in SAMPLE_CARS if c["pret"] <= budget * 1.1]

    return filtered


def _score_cars(cars: list[dict], profile: UserProfile) -> list[CarRecommendation]:
    """
    Calculează scorul de potrivire pentru fiecare mașină
    pe baza profilului utilizatorului.
    """
    results = []

    for car in cars:
        ratings = car["ratings"]

        # Scor ponderat: rating-ul mașinii * preferința utilizatorului
        score = (
            ratings["comfort"] * (profile.comfort / 100) +
            ratings["sport"] * (profile.sport / 100) +
            ratings["siguranta"] * (profile.siguranta / 100) +
            ratings["economie"] * (profile.economie / 100) +
            ratings["estetica"] * (profile.estetica / 100)
        )

        # Normalizare la 0-100
        max_possible = 5.0  # Rating maxim
        score_normalized = round((score / max_possible) * 100, 1)

        results.append(CarRecommendation(
            id=car["id"],
            marca=car["marca"],
            model=car["model"],
            an=car["an"],
            pret=car["pret"],
            tip_combustibil=car["tip_combustibil"],
            tip_caroserie=car["tip_caroserie"],
            score_total=score_normalized,
            score_details={
                "comfort": round(ratings["comfort"] * (profile.comfort / 100), 2),
                "sport": round(ratings["sport"] * (profile.sport / 100), 2),
                "siguranta": round(ratings["siguranta"] * (profile.siguranta / 100), 2),
                "economie": round(ratings["economie"] * (profile.economie / 100), 2),
                "estetica": round(ratings["estetica"] * (profile.estetica / 100), 2),
            }
        ))

    return results
