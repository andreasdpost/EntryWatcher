import pytest

from entrywatcher.config import RiskSettings
from entrywatcher.risk import PositionSizer, StopCalculator, StopLevel


def test_initial_stop_takes_the_lower_of_atr_and_swing_low():
    calc = StopCalculator(RiskSettings(atr_multiple=2.0, swing_low_buffer=0.01))
    assert calc.initial(100.0, 4.0, 95.0).price == pytest.approx(92.0)        # ATR tiefer
    assert calc.initial(100.0, 1.0, 90.0).price == pytest.approx(89.1)        # Tief tiefer
    assert calc.initial(100.0, 4.0, 95.0).distance == pytest.approx(0.08)


def test_trailing_stop_follows_highest_close_and_never_falls():
    calc = StopCalculator(RiskSettings(atr_multiple=2.0))
    assert calc.trailing(90.0, 120.0, 5.0) == pytest.approx(110.0)
    assert calc.trailing(90.0, 95.0, 5.0) == pytest.approx(90.0)


def test_size_is_limited_by_max_loss_or_max_position():
    sizer = PositionSizer(RiskSettings(max_position_eur=1000, max_loss_eur=100, max_stop_distance=0.10))
    wide = sizer.size(50.0, StopLevel(45.0, 0.10))            # 100/0.10 = 1000 → 20 Stück
    assert wide.shares == 20 and wide.risk == pytest.approx(100.0)
    tight = sizer.size(50.0, StopLevel(48.0, 0.04))           # 100/0.04 = 2500 → Deckel 1000
    assert tight.shares == 20 and tight.risk == pytest.approx(40.0)


def test_no_size_when_stop_too_far_or_share_too_expensive():
    sizer = PositionSizer(RiskSettings(max_position_eur=1000, max_loss_eur=100, max_stop_distance=0.10))
    assert sizer.size(50.0, StopLevel(44.0, 0.12)).shares == 0
    assert "kostet mehr" in sizer.size(1500.0, StopLevel(1400.0, 0.0667)).reason
