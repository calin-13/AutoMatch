from sqlalchemy import (
    Column, Integer, String, Float, DateTime, ForeignKey, Boolean,
    UniqueConstraint, func
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Car(Base):
    __tablename__ = "cars"

    id = Column(Integer, primary_key=True, index=True)
    marca = Column(String(50), nullable=False, index=True)
    model = Column(String(100), nullable=False)
    an = Column(Integer, nullable=False)
    pret = Column(Float, nullable=False)
    tip_combustibil = Column(String(20), nullable=False)
    tip_caroserie = Column(String(30), nullable=False)
    putere_cp = Column(Integer)
    consum_mediu = Column(Float)
    emisii_co2 = Column(Float)
    lungime_mm = Column(Integer)
    latime_mm = Column(Integer)
    inaltime_mm = Column(Integer)
    volum_portbagaj = Column(Integer)
    numar_locuri = Column(Integer, default=5)
    rating_siguranta = Column(Float)
    rating_comfort = Column(Float)
    rating_sport = Column(Float)
    rating_economie = Column(Float)
    rating_estetica = Column(Float)
    created_at = Column(DateTime, server_default=func.now())


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    recommendations = relationship("RecommendationHistory", back_populates="user")
    profile = relationship(
        "UserProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    feedbacks = relationship(
        "RecommendationFeedback",
        back_populates="user",
        cascade="all, delete-orphan",
    )


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id"), unique=True, nullable=False, index=True
    )

    inaltime = Column(Float, nullable=True)
    greutate = Column(Float, nullable=True)
    buget = Column(Float, nullable=True)
    km_zi = Column(Float, nullable=True)
    tip_combustibil = Column(String(20), nullable=True)

    score_comfort = Column(Float, nullable=True)
    score_sport = Column(Float, nullable=True)
    score_siguranta = Column(Float, nullable=True)
    score_economie = Column(Float, nullable=True)
    score_estetica = Column(Float, nullable=True)

    has_completed_test = Column(Boolean, default=False, nullable=False)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="profile")


class RecommendationHistory(Base):
    __tablename__ = "recommendation_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
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
    recommended_cars = Column(String(1000))
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="recommendations")


class RecommendationFeedback(Base):
    __tablename__ = "recommendation_feedback"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    car_id = Column(Integer, ForeignKey("cars.id"), nullable=False, index=True)
    recommendation_id = Column(
        Integer, ForeignKey("recommendation_history.id"), nullable=True, index=True
    )
    rating = Column(Integer, nullable=False)  # -1, 0, +1
    comment = Column(String(500), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="feedbacks")
    car = relationship("Car")

    __table_args__ = (
        UniqueConstraint("user_id", "car_id", "recommendation_id", name="uq_feedback_user_car_rec"),
    )
