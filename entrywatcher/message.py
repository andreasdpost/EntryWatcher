"""Text für Telegram und Konsole. Nur Darstellung."""

from __future__ import annotations

from html import escape

from .positions import PositionReport
from .watcher import BUY, Assessment


def _eur(x: float) -> str:
    return f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


class MessageFormatter:
    def assessment(self, a: Assessment) -> str:
        title = f"{escape(a.item.name or a.item.ticker)} ({a.item.ticker})"
        lines = [f"<b>{title}: {a.status}</b>", f"Schluss {_eur(a.close)} am {a.day:%d.%m.%Y}"]
        for c in a.checks:
            lines.append(f"{'✅' if c.passed else '❌'} {escape(c.name)}" + (f": {escape(c.detail)}" if c.detail else ""))
        if a.status == BUY:
            lines.append(f"→ Stop {_eur(a.stop.price)} ({a.stop.distance:.1%} unter Kurs)")
            lines.append(f"→ {a.size.shares} Stück ≈ {_eur(a.size.value)} €, Verlust bei Stop ≈ {_eur(a.size.risk)} €")
            lines.append("Nach dem Kauf: Stop-Loss-Order setzen und Position in data/positions.json eintragen.")
        elif a.size.reason:
            lines.append(f"→ Größe: {escape(a.size.reason)}")
        return "\n".join(lines)

    def position(self, p: PositionReport) -> str:
        pos = p.position
        title = f"{escape(pos.name or pos.ticker)} ({pos.ticker})"
        lines = [f"<b>{title}: {p.status}</b>",
                 f"Schluss {_eur(p.close)}, Kauf {_eur(pos.entry_price)}, {pos.shares} Stück, "
                 f"GuV {_eur(p.gain)} €",
                 f"Stop jetzt {_eur(p.stop)} (sichert {_eur(p.locked_in)} €) — in Scalable nachziehen"]
        if p.status != "HALTEN":
            lines.append("⚠️ Schluss unter dem Stop: verkaufen, so wie vor dem Kauf festgelegt.")
        return "\n".join(lines)
