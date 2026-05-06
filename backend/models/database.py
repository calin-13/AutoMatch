from sqlalchemy import (
    Column, Integer, String, Float, DateTime, ForeignKey, Boolean,
    UniqueConstraint, func, JSON
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

    recommendations_legacy = relationship("RecommendationHistory", back_populates="user")
    recommendations = relationship("Recommendation", back_populates="user", cascade="all, delete-orphan")
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
    test_responses = relationship(
        "TestResponse",
        back_populates="user",
        cascade="all, delete-orphan",
    )


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False, index=True)

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
    test_version_completed = Column(Integer, nullable=True)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="profile")


class RecommendationHistory(Base):
    """LEGACY: tabel vechi cu CSV string. Pastrat pentru compatibilitate."""
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

    user = relationship("User", back_populates="recommendations_legacy")


class Recommendation(Base):
    """Header pentru o sesiune de recomandare. Normalizat 3NF."""
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    profile_snapshot = Column(JSON, nullable=False)  # {physiological, behavioral, derived_profile}
    scoring_method = Column(String(20), nullable=False, default="ml")  # ml, rule_based
    has_feedback_reranking = Column(Boolean, default=False, nullable=False)
    total_candidates = Column(Integer, nullable=True)  # cate masini au trecut filtrarea
    created_at = Column(DateTime, server_default=func.now(), index=True)

    user = relationship("User", back_populates="recommendations")
    items = relationship(
        "RecommendationItem",
        back_populates="recommendation",
        cascade="all, delete-orphan",
        order_by="RecommendationItem.rank",
    )


class RecommendationItem(Base):
    """Detaliu per masina recomandata in cadrul unei sesiuni."""
    __tablename__ = "recommendation_items"

    id = Column(Integer, primary_key=True, index=True)
    recommendation_id = Column(Integer, ForeignKey("recommendations.id"), nullable=False, index=True)
    car_id = Column(Integer, ForeignKey("cars.id"), nullable=False, index=True)
    rank = Column(Integer, nullable=False)
    score_total = Column(Float, nullable=False)
    score_details = Column(JSON, nullable=True)  # contine rule_based, ml, shap, feedback_adjustment

    recommendation = relationship("Recommendation", back_populates="items")
    car = relationship("Car")

    __table_args__ = (
        UniqueConstraint("recommendation_id", "rank", name="uq_recitem_rec_rank"),
    )


class RecommendationFeedback(Base):
    __tablename__ = "recommendation_feedback"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    car_id = Column(Integer, ForeignKey("cars.id"), nullable=False, index=True)
    recommendation_id = Column(
        Integer, ForeignKey("recommendation_history.id"), nullable=True, index=True
    )
    rating = Column(Integer, nullable=False)
    comment = Column(String(500), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="feedbacks")
    car = relationship("Car")

    __table_args__ = (
        UniqueConstraint("user_id", "car_id", "recommendation_id", name="uq_feedback_user_car_rec"),
    )


class TestQuestion(Base):
    __tablename__ = "test_questions"

    id = Column(Integer, primary_key=True, index=True)
    version = Column(Integer, nullable=False, index=True)
    order_index = Column(Integer, nullable=False)
    text = Column(String(500), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    options = relationship(
        "TestOption",
        back_populates="question",
        cascade="all, delete-orphan",
        order_by="TestOption.order_index",
    )

    __table_args__ = (
        UniqueConstraint("version", "order_index", name="uq_question_version_order"),
    )


class TestOption(Base):
    __tablename__ = "test_options"

    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("test_questions.id"), nullable=False, index=True)
    order_index = Column(Integer, nullable=False)
    text = Column(String(500), nullable=False)
    scores = Column(JSON, nullable=False)

    question = relationship("TestQuestion", back_populates="options")


class TestResponse(Base):
    __tablename__ = "test_responses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    question_id = Column(Integer, ForeignKey("test_questions.id"), nullable=False, index=True)
    option_id = Column(Integer, ForeignKey("test_options.id"), nullable=False)
    test_version = Column(Integer, nullable=False)
    submission_id = Column(String(50), nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="test_responses")
    question = relationship("TestQuestion")
    option = relationship("TestOption")
