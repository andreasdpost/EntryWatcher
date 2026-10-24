import warnings

import pytest

from entrywatcher.quiet import _CATEGORY, quiet_yfinance


def _warn(module):
    warnings.warn_explicit("The inplace keyword in DataFrame.sort_index is deprecated", _CATEGORY,
                           filename="x.py", lineno=1, module=module)


def test_hides_only_the_yfinance_inplace_warning():
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        with quiet_yfinance():
            _warn("yfinance.multi")
            _warn("entrywatcher.rules")
    assert [str(w.message)[:20] for w in caught] == ["The inplace keyword "]


def test_filter_is_removed_after_the_block():
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        with quiet_yfinance():
            pass
        _warn("yfinance.utils")
    assert len(caught) == 1
