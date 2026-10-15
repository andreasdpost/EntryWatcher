# 05 – Ergebnisse

## Lauf 1 — 2026-10-15

Bericht von `python run_backtest.py`:

2006-01-01 bis 2026-10-15 (20.8 Jahre), 20 Aktien, je 1.000 € Budget (Gesamtkapital 20.000 €). Ohne Zinseszins: Gewinne werden nicht reinvestiert.

### Varianten (alle Aktien zusammen)

| Variante | Trades | GuV vor Steuer | Steuer | CAGR vor St. | CAGR nach St. |
|---|---:|---:|---:|---:|---:|
| Standard: Stop 2×ATR, ohne Bestätigung | 3233 | 12.608 € | 3.325 € | 2.4 % | 1.9 % |
| Stop 3×ATR, ohne Bestätigung | 1754 | 19.749 € | 5.209 € | 3.4 % | 2.7 % |
| Stop 2×ATR, mit Bestätigung | 1935 | 2.889 € | 1.188 € | 0.7 % | 0.4 % |
| Buy & Hold derselben Aktien | 20 | 1.194.410 € | 315.026 € | 21.8 % | 20.1 % |
| MSCI World (Kursindex, ohne Dividenden) | 1 | 57.725 € | 10.657 € | 6.7 % | 6.0 % |

### Je Aktie: Standard: Stop 2×ATR, ohne Bestätigung

| Aktie | Trades | Treffer | Ø Gewinn | Ø Verlust | schlechtester | GuV v. St. | investiert | Buy & Hold GuV |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| NVDA | 171 | 42.7 % | 110 € | -46 € | -97 € | 3.596 € | 47.2 % | 737.818 € |
| AAPL | 191 | 46.1 % | 68 € | -34 € | -104 € | 2.462 € | 54.8 % | 154.293 € |
| MSFT | 196 | 43.9 % | 42 € | -29 € | -109 € | 364 € | 56.9 % | 27.679 € |
| AMZN | 200 | 46.0 % | 68 € | -35 € | -90 € | 2.423 € | 55.7 % | 104.290 € |
| GOOGL | 220 | 41.8 % | 58 € | -29 € | -94 € | 1.625 € | 60.2 % | 30.829 € |
| ASML | 222 | 39.2 % | 65 € | -31 € | -68 € | 1.459 € | 53.7 % | 83.396 € |
| JNJ | 173 | 33.5 % | 36 € | -21 € | -102 € | -304 € | 49.3 % | 6.610 € |
| KO | 178 | 39.9 % | 31 € | -19 € | -37 € | 126 € | 51.7 % | 7.555 € |
| SAP.DE | 183 | 38.8 % | 45 € | -32 € | -184 € | -439 € | 48.4 % | 6.330 € |
| INTC | 138 | 36.2 % | 70 € | -36 € | -117 € | 347 € | 36.2 % | 5.232 € |
| PYPL | 75 | 44.0 % | 71 € | -37 € | -88 € | 783 € | 40.1 % | 539 € |
| NKE | 153 | 36.6 % | 53 € | -31 € | -98 € | 22 € | 44.0 % | 3.491 € |
| BAYN.DE | 150 | 41.3 % | 64 € | -35 € | -109 € | 892 € | 42.5 % | 1.214 € |
| BAS.DE | 179 | 35.8 % | 50 € | -32 € | -74 € | -413 € | 46.9 % | 3.231 € |
| VNA.DE | 104 | 36.5 % | 53 € | -28 € | -71 € | 157 € | 46.1 % | 1.312 € |
| DBK.DE | 147 | 33.3 % | 68 € | -38 € | -86 € | -417 € | 37.3 % | -237 € |
| ENR.DE | 29 | 31.0 % | 104 € | -69 € | -344 € | -436 € | 21.9 % | 4.925 € |
| IFX.DE | 192 | 40.6 % | 70 € | -42 € | -134 € | 672 € | 47.9 % | 7.942 € |
| VOW3.DE | 172 | 34.9 % | 76 € | -39 € | -97 € | 185 € | 42.9 % | 3.749 € |
| DTE.DE | 160 | 33.1 % | 42 € | -25 € | -71 € | -496 € | 43.4 % | 4.211 € |

### Bewertung

1. **Als Renditequelle taugen die Regeln nicht.** 1,9 % p. a. nach Steuer (Standard),
   gegen 6,0 % für den MSCI World und 20 % für Buy & Hold derselben Aktien.
   Buy & Hold ist durch NVIDIA verzerrt (738.000 € von 1,19 Mio. €), aber auch ohne
   die Sieger liegt es vorn.
2. **Das Risiko ist begrenzt.** Ø Verlust je Trade −19 bis −69 €, also unter den
   100 €. Ausreißer gibt es nur bei Kurslücken über den Stop: Siemens Energy
   −344 € (Absturz 2023), SAP −184 €.
3. **Bestätigung verschlechtert**, Stop 3×ATR verbessert (O-001).
4. **Zu viele Trades:** ~8 je Aktie und Jahr; der 2×ATR-Stop wird oft im
   normalen Rauschen ausgelöst.

Fazit: Der Wächter ist ein Werkzeug für **Disziplin und Risikobegrenzung**,
kein Renditebringer. Genau dafür ist er gedacht (docs/00).
