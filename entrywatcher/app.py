"""Verdrahtet Watchlist, Positionen, Statusvergleich und Versand. Keine eigene Rechnung."""

from __future__ import annotations

import logging

from .message import MessageFormatter
from .positions import PositionBook, PositionTracker
from .state import StateStore
from .telegram import TelegramNotifier
from .watcher import EntryWatcher

logger = logging.getLogger(__name__)


class WatchApp:
    def __init__(self, config, watcher: EntryWatcher, tracker: PositionTracker, book: PositionBook,
                 state: StateStore, notifier: TelegramNotifier, formatter: MessageFormatter | None = None) -> None:
        self._cfg = config
        self._watcher = watcher
        self._tracker = tracker
        self._book = book
        self._state = state
        self._notifier = notifier
        self._fmt = formatter or MessageFormatter()

    def run(self, always: bool = False) -> str:
        """Prüft alles, sendet Telegram für geänderte Einträge (oder alle mit always), gibt den ganzen Bericht zurück."""
        texts: dict[str, str] = {}
        status: dict[str, str] = {}
        held = {p.ticker for p in self._book.load()}
        for position in self._book.load():
            key = f"pos:{position.ticker}"
            try:
                report = self._tracker.report(position)
                texts[key], status[key] = self._fmt.position(report), f"{report.status}|{report.stop:.2f}"
            except Exception as exc:  # eine kaputte Position soll die anderen nicht verhindern
                texts[key], status[key] = f"{position.ticker}: Fehler {exc}", "FEHLER"
        for item in self._cfg.watchlist:
            if item.ticker in held:
                continue
            key = f"watch:{item.ticker}"
            try:
                a = self._watcher.assess(item)
                texts[key], status[key] = self._fmt.assessment(a), a.status
            except Exception as exc:
                logger.exception("Prüfung fehlgeschlagen: %s", item.ticker)
                texts[key], status[key] = f"{item.ticker}: Fehler {exc}", "FEHLER"

        old = self._state.load()
        to_send = sorted(texts) if always else StateStore.changed(old, status)
        if to_send:
            self._notifier.send("\n\n".join(texts[k] for k in to_send))
        self._state.save(status)
        return "\n\n".join(texts[k] for k in sorted(texts))
