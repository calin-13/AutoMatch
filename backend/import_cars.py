import csv
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.append(".")
from models.database import Base, Car
from config import DATABASE_URL

engine = create_engine(DATABASE_URL)
Base.metadata.create_all(bind=engine)
Session = sessionmaker(bind=engine)
session = Session()

session.query(Car).delete()
session.commit()

with open("data/cars_dataset.csv", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    cars = []
    for row in reader:
        car = Car(
            marca=row["marca"],
            model=row["model"],
            an=int(row["an"]),
            pret=float(row["pret"]),
            tip_combustibil=row["tip_combustibil"],
            tip_caroserie=row["tip_caroserie"],
            putere_cp=int(row["putere_cp"]),
            consum_mediu=float(row["consum_mediu"]),
            emisii_co2=float(row["emisii_co2"]),
            lungime_mm=int(row["lungime_mm"]),
            latime_mm=int(row["latime_mm"]),
            inaltime_mm=int(row["inaltime_mm"]),
            volum_portbagaj=int(row["volum_portbagaj"]),
            numar_locuri=int(row["numar_locuri"]),
            rating_siguranta=float(row["rating_siguranta"]),
            rating_comfort=float(row["rating_comfort"]),
            rating_sport=float(row["rating_sport"]),
            rating_economie=float(row["rating_economie"]),
            rating_estetica=float(row["rating_estetica"]),
        )
        cars.append(car)

session.bulk_save_objects(cars)
session.commit()
print(f"Importate {len(cars)} masini in baza de date.")
session.close()
