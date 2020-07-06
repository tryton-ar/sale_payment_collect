# The COPYRIGHT file at the top level of jhis repository contains the
# full copyright notices and license terms.

try:
    from trytond.modules.sale_payment_collect.tests.test_sale_payment_collect import suite
except ImportError:
    from .test_sale_payment_collect import suite

__all__ = ['suite']
