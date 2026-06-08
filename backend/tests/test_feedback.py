"""Teste unitare pentru ajustarea scorului pe baza feedback-ului anterior."""
from types import SimpleNamespace

import pytest

from services.feedback_service import compute_feedback_adjustment


def _car(cid, marca="BMW", model="Seria 5", caroserie="sedan",
         combustibil="benzina", pret=40000):
    return SimpleNamespace(id=cid, marca=marca, model=model,
                           tip_caroserie=caroserie, tip_combustibil=combustibil,
                           pret=pret)


def _fb(rating):
    return SimpleNamespace(rating=rating)


def _feedback_list(rating, n, **car_kwargs):
    return [(_fb(rating), _car(cid=1000 + i, **car_kwargs)) for i in range(n)]


def test_no_feedback_means_no_adjustment():
    assert compute_feedback_adjustment(_car(1), [])["adjustment"] == pytest.approx(0.0)


def test_liked_similar_cars_increase_score():
    res = compute_feedback_adjustment(
        _car(1), _feedback_list(1, 5, marca="BMW", caroserie="sedan",
                                combustibil="benzina", pret=40000))
    assert res["adjustment"] > 0
    assert res["adjustment"] <= 8.0


def test_disliked_similar_cars_decrease_score():
    res = compute_feedback_adjustment(
        _car(1), _feedback_list(-1, 5, marca="BMW", caroserie="sedan",
                                combustibil="benzina", pret=40000))
    assert res["adjustment"] < 0
    assert res["adjustment"] >= -8.0


def test_adjustment_is_capped_at_8():
    res = compute_feedback_adjustment(
        _car(1), _feedback_list(1, 30, marca="BMW", caroserie="sedan",
                                combustibil="benzina", pret=40000))
    assert res["adjustment"] <= 8.0


def test_confidence_grows_with_feedback_count():
    one = compute_feedback_adjustment(_car(1), _feedback_list(1, 1))
    five = compute_feedback_adjustment(_car(1), _feedback_list(1, 5))
    assert one["confidence"] < five["confidence"]
    assert five["confidence"] == pytest.approx(1.0)


def test_neutral_feedback_is_ignored():
    assert compute_feedback_adjustment(
        _car(1), _feedback_list(0, 5))["adjustment"] == pytest.approx(0.0)
