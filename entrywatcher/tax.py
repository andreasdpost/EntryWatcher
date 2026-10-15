"""Deutsche Abgeltungsteuer auf realisierte Gewinne, so wie die Depotbank sie abführt.

Abgebildet:
  * Teilfreistellung (Anteil des Gewinns/Verlusts, der steuerfrei bleibt)
  * Verlustverrechnung im laufenden Jahr: ein späterer Verlust erstattet
    bereits gezahlte Steuer desselben Jahres zurück
  * Verlustvortrag ins nächste Jahr
  * Sparerpauschbetrag je Kalenderjahr, angewandt nach der Verlustverrechnung

Übernommen aus leverageForTheLongRun (lflr/tax.py) über SectorEtfBot, unverändert.

NICHT abgebildet (docs/02_offene_fragen.md, O-005): Vorabpauschale.
"""

from __future__ import annotations

from .config import TaxRules


class GermanTaxAccount:
    def __init__(self, rules: TaxRules) -> None:
        self._rules = rules
        self._year: int | None = None
        self._year_net = 0.0          # Summe steuerpflichtiger Erträge im Jahr (nach Teilfreistellung)
        self._paid_this_year = 0.0
        self._loss_carry_in = 0.0     # Verlustvortrag zu Jahresbeginn
        self.total_paid = 0.0

    @property
    def loss_carry_forward(self) -> float:
        """Verlustvortrag, der am Ende des laufenden Jahres übrig bliebe."""
        if self._year_net < 0:
            return self._loss_carry_in - self._year_net
        return max(self._loss_carry_in - self._year_net, 0.0)

    def realize(self, gain: float, year: int, fund_income: bool = True) -> float:
        """Verbucht einen realisierten Gewinn (negativ = Verlust).

        fund_income=False für Zinsen auf Cash: dort gilt keine Teilfreistellung.
        Gibt die Zahlung zurück, die jetzt fällig wird: positiv = Steuer,
        negativ = Erstattung bereits gezahlter Steuer desselben Jahres.
        """
        self._roll_to(year)
        exemption = self._rules.partial_exemption if fund_income else 0.0
        self._year_net += gain * (1 - exemption)
        due_total = self._due_for_year()
        payment = due_total - self._paid_this_year
        self._paid_this_year = due_total
        self.total_paid += payment
        return payment

    def _due_for_year(self) -> float:
        after_losses = max(self._year_net - self._loss_carry_in, 0.0)
        taxable = max(after_losses - self._rules.annual_allowance, 0.0)
        return taxable * self._rules.effective_rate

    def _roll_to(self, year: int) -> None:
        if self._year is None:
            self._year = year
            return
        while self._year < year:
            self._loss_carry_in = self.loss_carry_forward
            self._year_net = 0.0
            self._paid_this_year = 0.0
            self._year += 1
