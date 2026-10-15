"""Letzter gemeldeter Status je Ticker, damit Telegram nur bei Änderungen schreibt."""

from __future__ import annotations

import json
from pathlib import Path


class StateStore:
    def __init__(self, path: Path | str) -> None:
        self._path = Path(path)

    def load(self) -> dict[str, str]:
        if not self._path.exists():
            return {}
        return json.loads(self._path.read_text(encoding="utf-8"))

    def save(self, state: dict[str, str]) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(json.dumps(state, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
                              encoding="utf-8")

    @staticmethod
    def changed(old: dict[str, str], new: dict[str, str]) -> list[str]:
        return sorted(k for k, v in new.items() if old.get(k) != v)
