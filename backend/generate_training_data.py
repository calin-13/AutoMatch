import numpy as np
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os

sys.path.append(".")
from config import DATABASE_URL
from models.database import Car

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

cars = session.query(Car).all()
print(f"Loaded {len(cars)} cars from database")

np.random.seed(42)

NUM_PROFILES = 30
profiles = []
for i in range(NUM_PROFILES):
    raw = np.random.dirichlet(np.ones(5)) * 100
    profiles.append({
        "profile_id": i,
        "pref_comfort": round(raw[0], 1),
        "pref_sport": round(raw[1], 1),
        "pref_siguranta": round(raw[2], 1),
        "pref_economie": round(raw[3], 1),
        "pref_estetica": round(raw[4], 1),
    })

training_data = []

for profile in profiles:
    budget = np.random.choice([15000, 25000, 40000, 60000, 100000, 300000])
    km_zi = np.random.choice([10, 30, 50, 80, 150])

    for car in cars:
        if car.pret > budget * 1.1:
            continue

        comfort_match = car.rating_comfort * (profile["pref_comfort"] / 100)
        sport_match = car.rating_sport * (profile["pref_sport"] / 100)
        safety_match = car.rating_siguranta * (profile["pref_siguranta"] / 100)
        economy_match = car.rating_economie * (profile["pref_economie"] / 100)
        aesthetic_match = car.rating_estetica * (profile["pref_estetica"] / 100)

        base_score = comfort_match + sport_match + safety_match + economy_match + aesthetic_match
        base_score_normalized = (base_score / 5.0) * 100

        bonus = 0

        if profile["pref_sport"] > 30 and car.putere_cp and car.putere_cp > 200:
            bonus += 5
        if profile["pref_sport"] > 30 and car.tip_caroserie == "coupe":
            bonus += 3

        if profile["pref_economie"] > 30 and car.consum_mediu and car.consum_mediu < 5.5:
            bonus += 5
        if profile["pref_economie"] > 30 and car.tip_combustibil in ("electric", "hybrid"):
            bonus += 3

        if profile["pref_comfort"] > 30 and car.volum_portbagaj and car.volum_portbagaj > 500:
            bonus += 4
        if profile["pref_comfort"] > 30 and car.tip_caroserie in ("sedan", "break", "suv"):
            bonus += 2

        if profile["pref_siguranta"] > 30 and car.rating_siguranta >= 4.5:
            bonus += 5
        if profile["pref_siguranta"] > 30 and car.tip_caroserie == "suv":
            bonus += 2

        if profile["pref_estetica"] > 30 and car.rating_estetica >= 4.5:
            bonus += 5
        if profile["pref_estetica"] > 30 and car.tip_caroserie == "coupe":
            bonus += 3

        if km_zi > 80 and car.consum_mediu and car.consum_mediu > 10:
            bonus -= 5
        if km_zi < 20 and car.tip_combustibil == "electric":
            bonus += 3

        price_ratio = car.pret / budget if budget > 0 else 1
        if 0.6 <= price_ratio <= 0.9:
            bonus += 3
        elif price_ratio < 0.3:
            bonus -= 3

        final_score = np.clip(base_score_normalized + bonus + np.random.normal(0, 2), 0, 100)
        final_score = round(final_score, 1)

        label = 0
        if final_score >= 75:
            label = 2
        elif final_score >= 55:
            label = 1

        training_data.append({
            "pref_comfort": profile["pref_comfort"],
            "pref_sport": profile["pref_sport"],
            "pref_siguranta": profile["pref_siguranta"],
            "pref_economie": profile["pref_economie"],
            "pref_estetica": profile["pref_estetica"],
            "budget": budget,
            "km_zi": km_zi,
            "car_pret": car.pret,
            "car_putere_cp": car.putere_cp or 0,
            "car_consum_mediu": car.consum_mediu or 0,
            "car_emisii_co2": car.emisii_co2 or 0,
            "car_volum_portbagaj": car.volum_portbagaj or 0,
            "car_numar_locuri": car.numar_locuri or 5,
            "car_rating_siguranta": car.rating_siguranta or 0,
            "car_rating_comfort": car.rating_comfort or 0,
            "car_rating_sport": car.rating_sport or 0,
            "car_rating_economie": car.rating_economie or 0,
            "car_rating_estetica": car.rating_estetica or 0,
            "car_is_electric": 1 if car.tip_combustibil == "electric" else 0,
            "car_is_hybrid": 1 if car.tip_combustibil == "hybrid" else 0,
            "car_is_suv": 1 if car.tip_caroserie == "suv" else 0,
            "car_is_coupe": 1 if car.tip_caroserie == "coupe" else 0,
            "car_is_sedan": 1 if car.tip_caroserie == "sedan" else 0,
            "price_ratio": round(car.pret / budget if budget > 0 else 1, 3),
            "score": final_score,
            "label": label,
        })

df = pd.DataFrame(training_data)

os.makedirs("ml", exist_ok=True)
df.to_csv("ml/training_data.csv", index=False)

print(f"Generated {len(df)} training samples")
print(f"\nLabel distribution:")
print(df["label"].value_counts().sort_index())
print(f"\nScore statistics:")
print(df["score"].describe())

session.close()
