"""Säule 3: Stop und Positionsgröße. Reine Rechnung, keine Daten, kein Netz."""

from __future__ import annotations

import math
from dataclasses import dataclass

from .config import RiskSettings


@dataclass(frozen=True)
class StopLevel:
    price: float
    distance: float      # Anteil unter dem Kurs, z. B. 0.088 = 8,8 %


class StopCalculator:
    """Anfangsstop = der tiefere von
      * Kurs − atr_multiple × ATR  (normale Schwankung der Aktie)
      * Tief der letzten swing_low_days Tage − Puffer  (letzte Struktur)
    Der tiefere Wert, damit der Stop nicht im normalen Rauschen liegt (E-004).
    """

    def __init__(self, risk: RiskSettings) -> None:
        self._risk = risk

    def initial(self, close: float, atr: float, swing_low: float) -> StopLevel:
        by_atr = close - self._risk.atr_multiple * atr
        by_structure = swing_low * (1 - self._risk.swing_low_buffer)
        price = min(by_atr, by_structure)
        return StopLevel(price, 1 - price / close)

    def trailing(self, initial_stop: float, highest_close: float, atr: float) -> float:
        """Nachgezogener Stop: steigt mit dem höchsten Schluss seit Kauf, fällt nie."""
        return max(initial_stop, highest_close - self._risk.atr_multiple * atr)


@dataclass(frozen=True)
class PositionSize:
    shares: int
    value: float
    risk: float          # Verlust, falls der Stop exakt greift
    reason: str = ""     # warum 0 Stück, falls 0


class PositionSizer:
    """Stückzahl = min(max_position, max_loss / Stop-Abstand) / Kurs, abgerundet (E-003)."""

    def __init__(self, risk: RiskSettings) -> None:
        self._risk = risk

    def size(self, price: float, stop: StopLevel) -> PositionSize:
        r = self._risk
        if stop.distance <= 0:
            return PositionSize(0, 0.0, 0.0, "Stop liegt nicht unter dem Kurs")
        if stop.distance > r.max_stop_distance:
            return PositionSize(0, 0.0, 0.0,
                                f"Stop {stop.distance:.1%} entfernt, erlaubt sind {r.max_stop_distance:.0%}")
        budget = min(r.max_position_eur, r.max_loss_eur / stop.distance)
        shares = math.floor(budget / price)
        if shares == 0:
            return PositionSize(0, 0.0, 0.0, f"Eine Aktie ({price:.2f}) kostet mehr als das Budget {budget:.0f}")
        return PositionSize(shares, shares * price, shares * (price - stop.price))
