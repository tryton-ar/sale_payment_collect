# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.

from trytond.model import fields
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval, If, Bool


class Sale(metaclass=PoolMeta):
    __name__ = 'sale.sale'

    paymode = fields.Many2One('payment.paymode', 'Paymode',
        domain=[
            ('party', '=', If(Bool(Eval('invoice_party',)),
                    Eval('invoice_party'), Eval('party'))),
            ],
        states={
            'readonly': Eval('state') != 'draft',
            })

    @fields.depends('party', 'invoice_party', 'paymode')
    def on_change_party(self):
        super(Sale, self).on_change_party()

        if not self.invoice_party:
            self.paymode = None
        if self.party:
            if not self.invoice_party:
                if self.party.customer_paymode:
                    self.paymode = self.party.customer_paymode

    @fields.depends('party', 'invoice_party', 'paymode')
    def on_change_invoice_party(self):
        super(Sale, self).on_change_invoice_party()

        self.paymode = None
        if self.invoice_party:
            if self.invoice_party.customer_paymode:
                self.paymode = self.invoice_party.customer_paymode
        elif self.party:
            if self.party.customer_paymode:
                self.paymode = self.party.customer_paymode

    def _get_invoice_sale(self):
        invoice = super(Sale, self)._get_invoice_sale()
        if invoice:
            invoice.paymode = self.paymode
        return invoice
