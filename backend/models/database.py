from sqlalchemy import Column, Integer, String, Float, DateTime, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Car(Base):
    """Modelul pentru mașinile din baza de date."""
    __tablename__ = "cars"

    id = Column(Integer, primary_key=True, index=True)
    marca = Column(String(50), nullable=False, index=True)
    model = Column(String(100), nullable=False)
    an = Column(Integer, nullable=False)
    pret = Column(Float, nullable=False)
    tip_combustibil = Column(String(20), nullable=False)  # benzina/diesel/electric/hybrid
    tip_caroserie = Column(String(30), nullable=False)     # sedan/suv/hatchback/coupe/break
    putere_cp = Column(Integer)
    consum_mediu = Column(Float)  # l/100km sau kWh/100km
    emisii_co2 = Column(Float)
    lungime_mm = Column(Integer)
    latime_mm = Column(Integer)
    inaltime_mm = Column(Integer)
    volum_portbagaj = Column(Integer)  # litri
    numar_locuri = Column(Integer, default=5)
    rating_siguranta = Column(Float)  # 0-5 (Euro NCAP)
    rating_comfort = Column(Float)    # 0-5
    rating_sport = Column(Float)      # 0-5
    rating_economie = Column(Float)   # 0-5
    rating_estetica = Column(Float)   # 0-5
    created_at = Column(DateTime, server_default=func.now())


class UserSession(Base):
    """Sesiunile utilizatorilor pentru tracking."""
    __tablename__ = "user_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), unique=True, nullable=False)
    inaltime = Column(Float)
    greutate = Column(Float)
    buget = Column(Float)
    km_zi = Column(Float)
    tip_combustibil = Column(String(20))
    score_comfort = Column(Float)
    score_sport = Column(Float)
    score_siguranta = Column(Float)
    score_economie = Column(Float)
    score_estetica = Column(Float)
    recommended_car_ids = Column(String(500))  # CSV of car IDs
    created_at = Column(DateTime, server_default=func.now())
