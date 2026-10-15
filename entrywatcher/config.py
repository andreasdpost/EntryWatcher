"""Konfiguration: typisierte Werte aus config/settings.toml."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, field, replace
from pathlib import Path

DEFAULT_PATH = Path(__file__).resolve().parent.parent / "config" / "settings.toml"


@dataclass(frozen=True)
class RiskSettings:
    max_position_eur: float = 1000.0
    max_loss_eur: float = 100.0
    max_stop_distance: float = 0.10
    atr_days: int = 14
    atr_multiple: float = 3.0
    swing_low_days: int = 10
    swing_low_buffer: float = 0.01


@dataclass(frozen=True)
class RuleSettings:
    market_ticker: str = "^990100-USD-STRD"
    trend_sma_days: int = 200
    fast_sma_days: int = 50
    momentum_days: int = 252
    momentum_skip_days: int = 21
    max_return_1m: float = 0.15
    max_above_fast_sma: float = 0.10
    earnings_block_days: int = 7
    confirmation: bool = False
    ema_days: int = 20
    pullback_days: int = 10


@dataclass(frozen=True)
class TaxRules:
    capital_gains_rate: float = 0.25
    solidarity_surcharge: float = 0.055
    church_tax_rate: float = 0.0
    partial_exemption: float = 0.0
    annual_allowance: float = 0.0

    @property
    def effective_rate(self) -> float:
        """Abgeltungsteuer + Soli + Kirchensteuer (§ 32d Abs. 1 EStG); ohne Kirche 26,375 %."""
        k = self.church_tax_rate
        base = self.capital_gains_rate / (1 + self.capital_gains_rate * k)
        return base * (1 + self.solidarity_surcharge + k)


@dataclass(frozen=True)
class BacktestSettings:
    start: str = "2005-01-01"
    fee_per_order: float = 1.0
    half_spread: float = 0.001
    tickers: tuple[str, ...] = ()
    benchmark: str = "^990100-USD-STRD"


@dataclass(frozen=True)
class WatchItem:
    ticker: str
    name: str = ""
    note: str = ""
    max_position_eur: float | None = None
    max_loss_eur: float | None = None

    def risk(self, default: RiskSettings) -> RiskSettings:
        """Risikowerte dieses Eintrags: eigene Angaben vor den Standardwerten."""
        overrides = {k: v for k, v in (("max_position_eur", self.max_position_eur),
                                       ("max_loss_eur", self.max_loss_eur)) if v is not None}
        return replace(default, **overrides)


@dataclass(frozen=True)
class AppConfig:
    risk: RiskSettings
    rules: RuleSettings
    tax: TaxRules
    backtest: BacktestSettings
    watchlist: tuple[WatchItem, ...] = field(default_factory=tuple)


class ConfigLoader:
    """Liest die TOML-Datei und baut daraus AppConfig. Sonst nichts."""

    def __init__(self, path: Path | str = DEFAULT_PATH) -> None:
        self._path = Path(path)

    def load(self) -> AppConfig:
        with self._path.open("rb") as fh:
            return self.from_dict(tomllib.load(fh))

    @staticmethod
    def from_dict(raw: dict) -> AppConfig:
        bt = dict(raw.get("backtest", {}))
        bt["tickers"] = tuple(bt.get("tickers", ()))
        return AppConfig(
            risk=RiskSettings(**raw.get("risk", {})),
            rules=RuleSettings(**raw.get("rules", {})),
            tax=TaxRules(**raw.get("tax", {})),
            backtest=BacktestSettings(**bt),
            watchlist=tuple(WatchItem(**w) for w in raw.get("watchlist", [])),
        )
