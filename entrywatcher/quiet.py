"""yfinance (≤ 1.7) ruft pandas mit `inplace=True` auf; pandas ≥ 3.1 warnt davor
(Pandas4Warning). Die Warnung betrifft nicht unseren Code. Hier wird genau diese
Warnung, nur aus yfinance, ausgeblendet — alle anderen bleiben sichtbar (E-018).
"""

from __future__ import annotations

import warnings
from contextlib import contextmanager

try:
    from pandas.errors import Pandas4Warning as _CATEGORY
except ImportError:  # pandas < 3.1 kennt die Klasse nicht und warnt auch nicht
    _CATEGORY = DeprecationWarning


@contextmanager
def quiet_yfinance():
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message="The inplace keyword", category=_CATEGORY,
                                module=r"yfinance(\..*)?$")
        yield
