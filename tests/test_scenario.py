"""Test scenario."""
from trytond.tests.test_tryton import load_doc_tests


def load_tests(loader, tests, pattern):
    return load_doc_tests(__name__, __file__, loader, tests, pattern)
