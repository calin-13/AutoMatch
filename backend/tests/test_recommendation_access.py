"""Istoricul de recomandari: numar fix de query-uri (fara N+1) si izolare intre useri."""
import os

os.environ.setdefault("DATABASE_URL", "sqlite://")
os.environ.setdefault("SECRET_KEY", "test-secret")

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from models.database import Base, Car, User, Recommendation, RecommendationItem
from api.auth_routes import list_recommendations, get_recommendation_detail


@pytest.fixture
def db():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    session.queries = []
    event.listen(
        engine, "before_cursor_execute",
        lambda conn, cur, sql, *a: session.queries.append(sql),
    )
    yield session
    session.close()


def _user(db, name):
    u = User(email=f"{name}@test.ro", username=name, hashed_password="x")
    db.add(u)
    db.flush()
    return u


def _recommendations(db, user, count):
    for i in range(count):
        car = Car(marca="Dacia", model=f"M{i}", an=2020, pret=10000,
                  tip_combustibil="benzina", tip_caroserie="sedan")
        rec = Recommendation(user_id=user.id, profile_snapshot={})
        rec.items = [RecommendationItem(car=car, rank=1, score_total=0.9)]
        db.add(rec)
    db.commit()


def _queries_for_list(db, user):
    db.expire_all()
    db.queries.clear()
    result = list_recommendations(current_user=user, db=db)
    return result, len(db.queries)


def test_list_query_count_does_not_grow_with_results(db):
    few, many = _user(db, "few"), _user(db, "many")
    _recommendations(db, few, 2)
    _recommendations(db, many, 20)

    small, small_queries = _queries_for_list(db, few)
    large, large_queries = _queries_for_list(db, many)

    assert small.total == 2 and large.total == 20
    assert large.recommendations[0].top_car_marca == "Dacia"
    assert small_queries == large_queries


def test_user_cannot_read_another_users_recommendation(db):
    owner, other = _user(db, "owner"), _user(db, "other")
    _recommendations(db, owner, 1)
    rec_id = db.query(Recommendation).filter_by(user_id=owner.id).one().id

    assert get_recommendation_detail(rec_id, current_user=owner, db=db).id == rec_id
    with pytest.raises(HTTPException) as err:
        get_recommendation_detail(rec_id, current_user=other, db=db)
    assert err.value.status_code == 404


def test_deleting_user_removes_legacy_history(db):
    from models.database import RecommendationHistory

    user = _user(db, "gone")
    _recommendations(db, user, 1)
    db.add(RecommendationHistory(user_id=user.id, recommended_cars="1"))
    db.commit()

    db.delete(user)
    db.commit()

    assert db.query(RecommendationHistory).count() == 0
