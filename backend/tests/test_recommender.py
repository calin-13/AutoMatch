"""Teste unitare pentru functiile pure ale motorului de recomandare."""
from types import SimpleNamespace

import pytest

from services.recommender import _similarity, _calculate_rule_based_score


def _car(marca="BMW", caroserie="sedan", combustibil="benzina",
         comfort=0, sport=0, siguranta=0, economie=0, estetica=0):
    return SimpleNamespace(
        marca=marca, tip_caroserie=caroserie, tip_combustibil=combustibil,
        rating_comfort=comfort, rating_sport=sport, rating_siguranta=siguranta,
        rating_economie=economie, rating_estetica=estetica,
    )


def _profile(comfort=20, sport=20, siguranta=20, economie=20, estetica=20):
    return SimpleNamespace(comfort=comfort, sport=sport, siguranta=siguranta,
                           economie=economie, estetica=estetica)


def test_similarity_identical_cars_is_one():
    assert _similarity(_car("BMW", "sedan", "benzina"),
                       _car("BMW", "sedan", "benzina")) == pytest.approx(1.0)


def test_similarity_all_different_is_zero():
    assert _similarity(_car("BMW", "sedan", "benzina"),
                       _car("Dacia", "suv", "diesel")) == pytest.approx(0.0)


def test_similarity_same_brand_only():
    assert _similarity(_car("BMW", "sedan", "benzina"),
                       _car("BMW", "suv", "diesel")) == pytest.approx(1.0 / 1.9)


def test_similarity_is_symmetric():
    a = _car("Audi", "coupe", "benzina")
    b = _car("Audi", "sedan", "benzina")
    assert _similarity(a, b) == pytest.approx(_similarity(b, a))


def test_similarity_is_normalized_between_0_and_1():
    s = _similarity(_car("BMW", "sedan", "diesel"), _car("BMW", "sedan", "benzina"))
    assert 0.0 <= s <= 1.0


def test_rule_score_perfect_match_is_100():
    car = _car(comfort=5, sport=5, siguranta=5, economie=5, estetica=5)
    assert _calculate_rule_based_score(car, _profile()) == pytest.approx(100.0)


def test_rule_score_zero_ratings_is_zero():
    assert _calculate_rule_based_score(_car(), _profile()) == pytest.approx(0.0)


def test_rule_score_known_value():
    car = _car(comfort=4, sport=2, siguranta=5, economie=1, estetica=3)
    assert _calculate_rule_based_score(car, _profile()) == pytest.approx(60.0)


def test_rule_score_in_valid_range():
    car = _car(comfort=4, sport=2, siguranta=5, economie=1, estetica=3)
    score = _calculate_rule_based_score(
        car, _profile(comfort=60, sport=10, siguranta=10, economie=10, estetica=10))
    assert 0.0 <= score <= 100.0
