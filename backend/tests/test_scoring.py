"""Teste unitare pentru derivarea profilului din date fiziologice + mini-test."""
from types import SimpleNamespace

import pytest

from services.scoring import calculate_rule_based_scores


def _input(inaltime=175, buget=20000, km_zi=30, combustibil="hibrid",
           comfort=10, sport=10, siguranta=10, economie=10, estetica=10):
    # valori neutre implicit: niciun bonus fiziologic -> profil echilibrat
    phys = SimpleNamespace(inaltime=inaltime, buget=buget, km_zi=km_zi,
                           tip_combustibil=combustibil)
    behav = SimpleNamespace(comfort=comfort, sport=sport, siguranta=siguranta,
                            economie=economie, estetica=estetica)
    return SimpleNamespace(physiological=phys, behavioral=behav)


def test_neutral_profile_is_balanced():
    p = calculate_rule_based_scores(_input())
    for axis in (p.comfort, p.sport, p.siguranta, p.economie, p.estetica):
        assert axis == pytest.approx(20.0)


def test_scores_sum_to_100():
    p = calculate_rule_based_scores(_input(inaltime=190))
    total = p.comfort + p.sport + p.siguranta + p.economie + p.estetica
    assert abs(total - 100.0) <= 1.0


def test_tall_person_gets_more_comfort():
    tall = calculate_rule_based_scores(_input(inaltime=190))
    base = calculate_rule_based_scores(_input(inaltime=175))
    assert tall.comfort > base.comfort


def test_low_budget_boosts_economy():
    low = calculate_rule_based_scores(_input(buget=8000))
    mid = calculate_rule_based_scores(_input(buget=20000))
    assert low.economie > mid.economie


def test_high_daily_km_boosts_economy():
    high = calculate_rule_based_scores(_input(km_zi=80))
    low = calculate_rule_based_scores(_input(km_zi=30))
    assert high.economie > low.economie


def test_electric_fuel_boosts_economy():
    electric = calculate_rule_based_scores(_input(combustibil="electric"))
    other = calculate_rule_based_scores(_input(combustibil="hibrid"))
    assert electric.economie > other.economie


def test_budget_category_mapping():
    assert calculate_rule_based_scores(_input(buget=3000)).categorie_buget == "economic"
    assert calculate_rule_based_scores(_input(buget=10000)).categorie_buget == "mediu"
    assert calculate_rule_based_scores(_input(buget=20000)).categorie_buget == "premium"
    assert calculate_rule_based_scores(_input(buget=50000)).categorie_buget == "lux"
    assert calculate_rule_based_scores(_input(buget=None)).categorie_buget == "flexibil"


def test_usage_category_mapping():
    assert calculate_rule_based_scores(_input(km_zi=10)).categorie_utilizare == "urban"
    assert calculate_rule_based_scores(_input(km_zi=40)).categorie_utilizare == "mixt"
    assert calculate_rule_based_scores(_input(km_zi=80)).categorie_utilizare == "extraurban"


def test_zero_behavioral_does_not_crash():
    p = calculate_rule_based_scores(
        _input(comfort=0, sport=0, siguranta=0, economie=0, estetica=0))
    assert p.comfort == 0.0
