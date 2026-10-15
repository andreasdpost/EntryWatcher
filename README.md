# EntryWatcher

Prüft jeden Abend die Aktien deiner Watchlist nach festen Regeln und meldet
per Telegram, wenn ein Kauf erlaubt ist — mit Stop-Kurs und Stückzahl. Für
gekaufte Aktien meldet er den nachgezogenen Stop und wann verkauft werden muss.

Nur für den Satelliten (≈ 10 % des Depots). Der Wächter **kauft nicht**,
du entscheidest und handelst selbst bei Scalable.

> **Erwartung:** Im Backtest bringen die Regeln wenig Rendite (≈ 2 % p. a. nach
> Steuer), begrenzen aber jeden Fehlkauf auf rund 100 €. Siehe [docs/05](docs/05_ergebnisse.md).

## So benutzt du ihn

1. **Aktie beobachten:** in `config/settings.toml` einen Block `[[watchlist]]`
   anlegen. Deutsche Kürzel nehmen (Yahoo-Symbol mit `.DE`, z. B. `NVD.DE`),
   damit Kurse in Euro sind.
2. **Meldung „KAUFEN ERLAUBT“:** Stückzahl kaufen, sofort eine
   **Stop-Loss-Order** zum gemeldeten Stop setzen.
3. **Kauf eintragen** in `data/positions.json`:
   ```json
   [{"ticker": "ENR.DE", "name": "Siemens Energy", "entry_date": "2026-11-03",
     "entry_price": 131.20, "shares": 7, "initial_stop": 119.50}]
   ```
4. **Meldung neuer Stop:** Stop-Order in Scalable nachziehen.
   **Meldung „VERKAUFEN“:** verkaufen (falls die Stop-Order nicht schon gegriffen hat)
   und die Position aus `positions.json` löschen.

## Doku

| | |
|---|---|
| [00 Ausgangslage](docs/00_ausgangslage.md) | Warum es das gibt |
| [01 Entscheidungen](docs/01_entscheidungen.md) | Was entschieden wurde und warum |
| [02 Offene Fragen](docs/02_offene_fragen.md) | Was noch offen ist |
| [03 Methodik](docs/03_methodik.md) | Regeln, Stop, Größe, Backtest |
| [04 Architektur](docs/04_architektur.md) | Klassen und Aufgaben |
| [05 Ergebnisse](docs/05_ergebnisse.md) | Backtest-Läufe |

## Lokal

```bash
python -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/pytest -q
.venv/bin/python run_watch.py --no-telegram     # heutige Prüfung
.venv/bin/python run_backtest.py                # Backtest → reports/backtest.md
```

## GitHub Actions

| Workflow | Wann | Was |
|---|---|---|
| `daily_watch.yml` | Mo–Fr 21:30 UTC + manuell | Prüfung, Telegram bei Änderung |
| `backtest.yml` | manuell | Bericht als Artefakt |
| `tests.yml` | jeder Push | `pytest` |

Secrets unter *Settings → Secrets and variables → Actions*: `TELEGRAM_TOKEN`, `TELEGRAM_CHAT_ID`
(dieselben wie in den anderen Repos).

> Keine Anlageberatung.
