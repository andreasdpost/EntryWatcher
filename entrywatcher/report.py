"""Markdown-Bericht des Backtests. Nur Darstellung."""

from __future__ import annotations

import pandas as pd


def pct(x: float) -> str:
    return f"{x * 100:.1f} %"


def eur(x: float) -> str:
    return f"{x:,.0f} €".replace(",", ".")


class BacktestReport:
    def render(self, results, bh: pd.DataFrame, start, end, capital_per_ticker: float) -> str:
        years = results[0].years
        capital = results[0].capital
        n = len(bh)
        rate = bh.attrs["rate"]
        bh_gain = bh["gain"].sum()
        bh_after = bh_gain - max(bh_gain, 0) * rate      # vereinfacht: Gewinne/Verluste gegeneinander verrechnet
        msci = bh.attrs["msci_gain"]
        msci_after = msci - max(msci, 0) * rate * 0.7     # ETF: 30 % Teilfreistellung
        cagr = lambda g: ((capital + g) / capital) ** (1 / years) - 1
        out = [
            "# Backtest EntryWatcher", "",
            f"{start:%Y-%m-%d} bis {end:%Y-%m-%d} ({years:.1f} Jahre), {n} Aktien, je {eur(capital_per_ticker)} Budget "
            f"(Gesamtkapital {eur(capital)}). Ohne Zinseszins: Gewinne werden nicht reinvestiert.", "",
            "## Varianten (alle Aktien zusammen)", "",
            "| Variante | Trades | GuV vor Steuer | Steuer | CAGR vor St. | CAGR nach St. |",
            "|---|---:|---:|---:|---:|---:|",
        ]
        for r in results:
            out.append(f"| {r.variant.label} | {len(r.trades)} | {eur(r.gain_before_tax)} | {eur(r.taxes)} | "
                       f"{pct(r.cagr(False))} | {pct(r.cagr(True))} |")
        out.append(f"| Buy & Hold derselben Aktien | {n} | {eur(bh_gain)} | {eur(bh_gain - bh_after)} | "
                   f"{pct(cagr(bh_gain))} | {pct(cagr(bh_after))} |")
        out.append(f"| MSCI World (Kursindex, ohne Dividenden) | 1 | {eur(msci)} | {eur(msci - msci_after)} | "
                   f"{pct(cagr(msci))} | {pct(cagr(msci_after))} |")
        base = results[0]
        out += ["", f"## Je Aktie: {base.variant.label}", "",
                "| Aktie | Trades | Treffer | Ø Gewinn | Ø Verlust | schlechtester | GuV v. St. | investiert | Buy & Hold GuV |",
                "|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
        merged = base.per_ticker.merge(bh, on="ticker", suffixes=("", "_bh"))
        for _, r in merged.iterrows():
            out.append(f"| {r['ticker']} | {r['trades']} | {pct(r['hit_rate'])} | {eur(r['avg_win'])} | "
                       f"{eur(r['avg_loss'])} | {eur(r['worst'])} | {eur(r['gain'])} | {pct(r['invested_time'])} | "
                       f"{eur(r['gain_bh'])} |")
        return "\n".join(out) + "\n"
