"""Telegram-Versand über die Bot-API. Übernommen aus leverageForTheLongRun (lflr/telegram.py), dort aus cryptoSignumBot.

send() wirft nie: ein Versandfehler wird geloggt und als False gemeldet.
Der Token wird nie geloggt.
"""

from __future__ import annotations

import logging
import os

import httpx

logger = logging.getLogger(__name__)

_API_URL = "https://api.telegram.org/bot{token}/sendMessage"
_MAX_LENGTH = 4096


class TelegramNotifier:
    def __init__(self, token: str | None, chat_id: str | None, timeout: float = 10.0) -> None:
        self._token = token
        self._chat_id = chat_id
        self._timeout = timeout

    @classmethod
    def from_env(cls) -> "TelegramNotifier":
        return cls(os.getenv("TELEGRAM_TOKEN"), os.getenv("TELEGRAM_CHAT_ID"))

    @property
    def enabled(self) -> bool:
        return bool(self._token and self._chat_id)

    def send(self, text: str) -> bool:
        if not self.enabled:
            logger.info("Telegram nicht konfiguriert — Nachricht nicht gesendet.")
            return False
        if len(text) > _MAX_LENGTH:
            text = text[: _MAX_LENGTH - 20] + "\n… (gekürzt)"
        try:
            response = httpx.post(
                _API_URL.format(token=self._token),
                json={"chat_id": self._chat_id, "text": text, "parse_mode": "HTML"},
                timeout=self._timeout,
            )
        except httpx.HTTPError as exc:
            logger.warning("Telegram-Versand fehlgeschlagen: %s", exc)
            return False
        if response.status_code != 200:
            logger.warning("Telegram-Versand fehlgeschlagen: HTTP %s %s",
                           response.status_code, response.text[:200])
            return False
        return True
