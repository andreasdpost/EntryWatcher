# 02 – Offene Fragen

| ID | Frage | Wirkung | Stand |
|---|---|---|---|
| O-001 | Stop 3×ATR statt 2×ATR? Im Backtest besser (2,7 % statt 1,9 % CAGR n. St.), dann aber öfter Stop-Abstand > 10 % → weniger Käufe | Standard bleibt 2×ATR, bis der Nutzer entscheidet | entschieden: 3×ATR (E-015) |
| O-002 | Quartalszahlen-Regel gibt es nur live; Yahoo liefert keine historischen Termine | Backtest ohne diese Regel | bekannt |
| O-003 | Währung: Budget in €, US-Aktien kosten USD. Live sollten deutsche Börsenkürzel (z. B. `NVD.DE`) in die Watchlist; im Backtest werden USD wie € behandelt | Größe bei US-Kürzeln um den Wechselkurs falsch | offen |
| O-004 | Ausführung: Signal am Schluss, Kauf zum Schluss des Folgetags. Live kaufst du am Folgetag zu irgendeinem Kurs | Kleine Abweichung | bekannt |
| O-005 | Gewinne werden im Backtest nicht reinvestiert (Budget fest 1.000 €), Buy & Hold dagegen wächst mit | Benachteiligt die Regeln etwas | bewusst so (feste Größe ist die Vorgabe) |
| O-006 | Abgleich `positions.json` mit Scalable automatisch (wie in scalableBrokerAnalyzer) | Bequemlichkeit | später |
