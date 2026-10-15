# 03 – Methodik

## Tägliche Prüfung je Aktie der Watchlist

Alle Werte aus Tagesschlusskursen bis einschließlich heute.

| Regel | Bedingung |
|---|---|
| Markt | MSCI World (Kursindex) über seiner 200-Tage-Linie |
| Trend | Schluss > 200-Tage-Linie und 50-Tage-Linie > 200-Tage-Linie |
| Momentum | Rendite von vor 12 Monaten bis vor 1 Monat > 0 |
| Nicht überhitzt | Rendite letzter Monat (21 Handelstage) < +15 % |
| Nicht überdehnt | Schluss höchstens 10 % über der 50-Tage-Linie |
| Termin | keine Quartalszahlen in den nächsten 7 Tagen (nur live) |
| Bestätigung (aus) | Tief ≤ EMA20 in den letzten 10 Tagen, heute Schluss > EMA20 und > Vortageshoch |
| Stop-Abstand | Anfangsstop höchstens 10 % unter dem Schluss |

Status **KAUFEN ERLAUBT**, wenn alle Regeln erfüllt sind und mindestens eine Aktie ins Budget passt; sonst **WARTEN**.

## Stop und Größe

- ATR(14) = Durchschnitt der „wahren Spanne“ der letzten 14 Tage (Hoch − Tief, inkl. Lücken zum Vortagesschluss).
- Anfangsstop = min(Schluss − 2 × ATR, 10-Tage-Tief × 0,99).
- Stückzahl = abrunden(min(1.000 €, 100 € / Stop-Abstand) / Kurs).
- Nach dem Kauf: Stop = max(Anfangsstop, höchster Schluss seit Kauf − 2 × ATR). Fällt der Schluss darunter → **VERKAUFEN**.
  In Scalable setzt du den Stop als Stop-Loss-Order und ziehst ihn nach, wenn der Wächter einen neuen Wert meldet.

## Backtest

- 20 Aktien (Gewinner und Verlierer), 2006 bis heute, je 1.000 € Budget, nicht reinvestiert.
- Einstieg zum Schluss des Tages nach dem Signal; Ausstieg wie eine Stop-Loss-Order (E-010).
- Kosten: 1 € je Order, halbe Spanne 0,1 %. Steuer über ein gemeinsames Steuerkonto (E-011).
- Vergleich: Buy & Hold derselben Aktien (am Ende versteuert) und MSCI World (Kursindex, 30 % Teilfreistellung).
