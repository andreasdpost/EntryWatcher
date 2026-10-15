# 01 – Entscheidungen

Neue Einträge unten anhängen; alte nicht umschreiben, sondern ablösen.

| ID | Datum | Entscheidung | Begründung | Von |
|---|---|---|---|---|
| E-001 | 2026-10-15 | Eigenes Repo `EntryWatcher`, nur für den Satelliten | ETF-Kern bleibt unberührt; SectorEtfBot ist ein abgeschlossenes Projekt | Nutzer |
| E-002 | 2026-10-15 | Der Wächter entscheidet nicht, er prüft. Gekauft und verkauft wird von Hand bei Scalable | Ziel ist planvolles Handeln, keine Order-API | Nutzer |
| E-003 | 2026-10-15 | Größe: höchstens **1.000 €** je Position, höchstens **100 €** Verlust, wenn der Stop greift. Stückzahl = min(1.000, 100 / Stop-Abstand) / Kurs. Stop weiter als **10 %** entfernt → kein Kauf | Nutzervorgabe „1.000 € und max. 10 % Verlust“, als Risiko-Budget ausgelegt (Lesart B im Gespräch) | Nutzer/Claude |
| E-004 | 2026-10-15 | Anfangsstop = tieferer Wert aus *Kurs − 2 × ATR(14)* und *Tief der letzten 10 Tage − 1 %*. Danach nachgezogen: höchster Schluss seit Kauf − 2 × ATR, nie fallend | ATR passt den Stop an die normale Schwankung der Aktie an; pauschale −10 % tun das nicht | Claude |
| E-005 | 2026-10-15 | Einstiegsregeln: Markt (MSCI World) über 200-Tage-Linie; Aktie über 200er und 50er über 200er; Momentum 12 Monate ohne letzten Monat positiv; letzter Monat unter +15 %; höchstens 10 % über der 50er; keine Quartalszahlen in 7 Tagen | Säule 4 und die eigenen Fehler 2026 (Kauf nach Sprüngen). Grenzwerte vorab gesetzt, nicht optimiert | gemeinsam |
| E-006 | 2026-10-15 | Bestätigungsregel (Rücksetzer an EMA20, Schluss darüber und über Vortageshoch) ist eingebaut, aber **aus** (`rules.confirmation = false`) | Backtest: schlechter bei 9 von 10 Aktien (Vortest), Lauf 1: 0,4 % statt 1,9 % CAGR nach Steuer | Regel |
| E-007 | 2026-10-15 | Eine Regel für alle Aktien, **keine Parameter je Aktie** | Parameter je Aktie passen sich der Vergangenheit dieser Aktie an (Überanpassung) | Claude |
| E-008 | 2026-10-15 | Backtest über 20 Aktien, bewusst mit Verlierern (Intel, PayPal, Nike, Bayer, BASF, Vonovia, Deutsche Bank, VW, …), nicht nur bekannten Siegern | Nur Sieger zu testen macht Buy & Hold unschlagbar und sagt wenig über die Regeln | Claude |
| E-009 | 2026-10-15 | Gekaufte Positionen trägst du selbst in `data/positions.json` ein; der Wächter meldet dann den nachgezogenen Stop | Wie im Leverage-Repo: die Wahrheit steht in der Datei. Scalable-Abgleich später möglich | Claude |
| E-010 | 2026-10-15 | Ausstieg im Backtest wie eine echte Stop-Loss-Order: Tagestief ≤ Stop → Verkauf zum Stop, bei Kurslücke zum Eröffnungskurs | Realistischer als Verkauf zum Schluss; zeigt das Lückenrisiko (z. B. Siemens Energy 2023) | Claude |
| E-011 | 2026-10-15 | Steuer im Backtest: alle Verkäufe aller Aktien zeitlich geordnet durch ein Steuerkonto, 26,375 %, keine Teilfreistellung (Aktien) | Wie im echten Depot: Verluste werden mit Gewinnen verrechnet | Claude |
| E-012 | 2026-10-15 | Täglicher Lauf Mo–Fr 21:30 UTC per GitHub Action, Telegram nur bei Statusänderung; Status in `data/state.json` | Wie in den anderen Repos; keine Nachrichtenflut | Claude |
| E-013 | 2026-10-15 | Erste Aktie der Watchlist: **Siemens Energy** (ENR.DE) | Nutzerwunsch | Nutzer |
| E-014 | 2026-10-15 | Push direkt auf `main` für den ersten Stand | Repo war leer | Claude |
