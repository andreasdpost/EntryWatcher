import pytest

from entrywatcher.config import TaxRules
from entrywatcher.tax import GermanTaxAccount

RATE = 0.26375


def test_gain_is_taxed_at_effective_rate():
    acc = GermanTaxAccount(TaxRules())
    assert acc.realize(1000.0, 2020) == pytest.approx(1000 * RATE)


def test_partial_exemption_reduces_taxable_gain():
    acc = GermanTaxAccount(TaxRules(partial_exemption=0.30))
    assert acc.realize(1000.0, 2020) == pytest.approx(700 * RATE)


def test_partial_exemption_does_not_apply_to_interest():
    acc = GermanTaxAccount(TaxRules(partial_exemption=0.30))
    assert acc.realize(100.0, 2020, fund_income=False) == pytest.approx(100 * RATE)


def test_loss_later_in_year_refunds_tax_paid_earlier():
    acc = GermanTaxAccount(TaxRules())
    paid = acc.realize(1000.0, 2020)
    refund = acc.realize(-400.0, 2020)
    assert refund == pytest.approx(-400 * RATE)
    assert acc.total_paid == pytest.approx(paid + refund) == pytest.approx(600 * RATE)


def test_refund_never_exceeds_tax_paid_in_that_year():
    acc = GermanTaxAccount(TaxRules())
    acc.realize(100.0, 2020)
    assert acc.realize(-1000.0, 2020) == pytest.approx(-100 * RATE)
    assert acc.loss_carry_forward == pytest.approx(900.0)


def test_loss_is_carried_into_next_year():
    acc = GermanTaxAccount(TaxRules())
    assert acc.realize(-500.0, 2020) == 0.0
    assert acc.realize(800.0, 2021) == pytest.approx(300 * RATE)
    assert acc.loss_carry_forward == 0.0


def test_loss_carry_survives_empty_years():
    acc = GermanTaxAccount(TaxRules())
    acc.realize(-500.0, 2018)
    assert acc.realize(500.0, 2022) == pytest.approx(0.0)


def test_allowance_applies_per_year_after_loss_offset():
    acc = GermanTaxAccount(TaxRules(annual_allowance=1000.0))
    assert acc.realize(1500.0, 2020) == pytest.approx(500 * RATE)
    assert acc.realize(800.0, 2021) == pytest.approx(0.0)       # neuer Pauschbetrag
    acc2 = GermanTaxAccount(TaxRules(annual_allowance=1000.0))
    acc2.realize(-600.0, 2020)
    # 2021: 2000 Gewinn − 600 Vortrag − 1000 Pauschbetrag = 400 steuerpflichtig
    assert acc2.realize(2000.0, 2021) == pytest.approx(400 * RATE)
