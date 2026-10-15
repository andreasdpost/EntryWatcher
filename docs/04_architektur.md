# 04 – Architektur

Eine Klasse je Aufgabe. Rechnung kennt keine Darstellung, Darstellung rechnet nicht.

| Modul | Klasse | Aufgabe |
|---|---|---|
| `config.py` | `ConfigLoader`, `AppConfig`, `RiskSettings`, `RuleSettings`, `WatchItem` | `config/settings.toml` lesen |
| `market_data.py` | `YahooPriceSource`, `CsvPriceSource`, `CachedPriceSource` | Kurse (Open/High/Low/Close) laden und zwischenspeichern |
| `indicators.py` | `Indicators`, `market_uptrend` | Linien, ATR, Renditen je Tag |
| `rules.py` | `Rule` und je Regel eine Klasse, `RuleSet` | Einstiegsregeln, als Reihe (Backtest) und für einen Tag (Meldung) |
| `risk.py` | `StopCalculator`, `PositionSizer` | Säule 3: Stop und Stückzahl |
| `earnings.py` | `YahooEarningsCalendar` | nächster Termin für Quartalszahlen |
| `watcher.py` | `EntryWatcher`, `Assessment` | eine Aktie prüfen → KAUFEN ERLAUBT / WARTEN |
| `positions.py` | `PositionBook`, `PositionTracker`, `PositionReport` | gekaufte Aktien: nachgezogener Stop, HALTEN / VERKAUFEN |
| `state.py` | `StateStore` | letzter Status, damit nur Änderungen gemeldet werden |
| `message.py` | `MessageFormatter` | Text für Telegram |
| `telegram.py` | `TelegramNotifier` | Versand (kopiert aus leverageForTheLongRun) |
| `app.py` | `WatchApp` | täglicher Lauf |
| `backtest.py` | `TradeSimulator`, `Trade`, `taxes_paid` | Regeln über die Historie |
| `tax.py` | `GermanTaxAccount` | Abgeltungsteuer (kopiert) |
| `backtest_app.py`, `report.py` | `BacktestApp`, `BacktestReport` | Varianten rechnen, Bericht |

Tests in `tests/` laufen ohne Netz auf synthetischen Kursen.
