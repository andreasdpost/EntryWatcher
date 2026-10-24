"""Nächster Termin für Quartalszahlen. Nur live, im Backtest nicht verfügbar (O-002)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date

from .quiet import quiet_yfinance


class EarningsCalendar(ABC):
    @abstractmethod
    def next_date(self, ticker: str) -> date | None:
        """Nächster bekannter Termin oder None, wenn unbekannt."""


class YahooEarningsCalendar(EarningsCalendar):
    def next_date(self, ticker: str) -> date | None:
        try:
            import yfinance as yf

            with quiet_yfinance():
                dates = yf.Ticker(ticker).calendar.get("Earnings Date") or []
            return dates[0] if dates else None
        except Exception:  # Termin ist ein Zusatz; ohne ihn läuft die Prüfung weiter
            return None
