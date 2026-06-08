"""Teste unitare pentru agregarea scorurilor mini-testului comportamental."""
from types import SimpleNamespace

from services.test_service import aggregate_scores_from_options


def _opt(scores):
    return SimpleNamespace(scores=scores)


def test_empty_options_returns_zero_axes():
    result = aggregate_scores_from_options([])
    assert result == {"comfort": 0, "sport": 0, "siguranta": 0,
                      "economie": 0, "estetica": 0}


def test_single_option_sums_its_axes():
    result = aggregate_scores_from_options([_opt({"siguranta": 3, "comfort": 1})])
    assert result["siguranta"] == 3
    assert result["comfort"] == 1
    assert result["sport"] == 0


def test_multiple_options_accumulate():
    opts = [_opt({"economie": 3, "comfort": 1}), _opt({"economie": 2, "sport": 1})]
    result = aggregate_scores_from_options(opts)
    assert result["economie"] == 5
    assert result["comfort"] == 1
    assert result["sport"] == 1


def test_unknown_axis_is_ignored():
    result = aggregate_scores_from_options([_opt({"inexistent": 99, "sport": 2})])
    assert "inexistent" not in result
    assert result["sport"] == 2


def test_none_scores_are_handled():
    result = aggregate_scores_from_options([_opt(None)])
    assert sum(result.values()) == 0
