=============================
Sale Payment Collect Scenario
=============================

Imports::

    >>> import datetime
    >>> from dateutil.relativedelta import relativedelta
    >>> from decimal import Decimal
    >>> from operator import attrgetter
    >>> from proteus import Model, Wizard, Report
    >>> from trytond.tests.tools import activate_modules, set_user
    >>> from trytond.modules.company.tests.tools import create_company, \
    ...     get_company
    >>> from trytond.modules.account.tests.tools import create_fiscalyear, \
    ...     create_chart, get_accounts, create_tax
    >>> from trytond.modules.account_invoice.tests.tools import \
    ...     set_fiscalyear_invoice_sequences, create_payment_term
    >>> today = datetime.date.today()

Activate modules::

    >>> config = activate_modules('sale_payment_collect')

Create company::

    >>> _ = create_company()
    >>> company = get_company()

Set employee::

    >>> User = Model.get('res.user')
    >>> Party = Model.get('party.party')
    >>> Employee = Model.get('company.employee')
    >>> employee_party = Party(name="Employee")
    >>> employee_party.save()
    >>> employee = Employee(party=employee_party)
    >>> employee.save()
    >>> user = User(config.user)
    >>> user.employees.append(employee)
    >>> user.employee = employee
    >>> user.save()
    >>> set_user(user.id)

Create fiscal year::

    >>> fiscalyear = set_fiscalyear_invoice_sequences(
    ...     create_fiscalyear(company))
    >>> fiscalyear.click('create_period')

Create chart of accounts::

    >>> _ = create_chart(company)
    >>> accounts = get_accounts(company)
    >>> revenue = accounts['revenue']
    >>> expense = accounts['expense']
    >>> cash = accounts['cash']

    >>> Journal = Model.get('account.journal')
    >>> PaymentMethod = Model.get('account.invoice.payment.method')
    >>> cash_journal, = Journal.find([('type', '=', 'cash')])
    >>> cash_journal.save()
    >>> payment_method = PaymentMethod()
    >>> payment_method.name = 'Cash'
    >>> payment_method.journal = cash_journal
    >>> payment_method.credit_account = cash
    >>> payment_method.debit_account = cash
    >>> payment_method.save()

Create tax::

    >>> tax = create_tax(Decimal('.10'))
    >>> tax.save()

Create parties::

    >>> Party = Model.get('party.party')
    >>> supplier = Party(name='Supplier')
    >>> supplier.save()
    >>> customer = Party(name='Customer')
    >>> customer.save()

Create paymode method::

    >>> Paymode = Model.get('payment.paymode')
    >>> paymode = Paymode()
    >>> paymode.party = customer
    >>> paymode.type = ''
    >>> paymode.credit_number = '5896570000000008'
    >>> paymode.save()

Create paymode2 method::

    >>> Paymode = Model.get('payment.paymode')
    >>> paymode2 = Paymode()
    >>> paymode2.party = customer
    >>> paymode2.type = ''
    >>> paymode2.credit_number = '4485715860868875'
    >>> paymode2.save()

Set up paymode to party::

    >>> customer.customer_paymode = paymode
    >>> customer.save()

Create account categories::

    >>> ProductCategory = Model.get('product.category')
    >>> account_category = ProductCategory(name="Account Category")
    >>> account_category.accounting = True
    >>> account_category.account_expense = expense
    >>> account_category.account_revenue = revenue
    >>> account_category.save()

    >>> account_category_tax, = account_category.duplicate()
    >>> account_category_tax.customer_taxes.append(tax)
    >>> account_category_tax.save()

Create product::

    >>> ProductUom = Model.get('product.uom')
    >>> unit, = ProductUom.find([('name', '=', 'Unit')])
    >>> ProductTemplate = Model.get('product.template')

    >>> template = ProductTemplate()
    >>> template.name = 'product'
    >>> template.default_uom = unit
    >>> template.type = 'goods'
    >>> template.salable = True
    >>> template.list_price = Decimal('10')
    >>> template.account_category = account_category_tax
    >>> template.save()
    >>> product, = template.products

    >>> template = ProductTemplate()
    >>> template.name = 'service'
    >>> template.default_uom = unit
    >>> template.type = 'service'
    >>> template.salable = True
    >>> template.list_price = Decimal('30')
    >>> template.account_category = account_category
    >>> template.save()
    >>> service, = template.products

Create payment term::

    >>> payment_term = create_payment_term()
    >>> payment_term.save()

Create an Inventory::

    >>> Inventory = Model.get('stock.inventory')
    >>> Location = Model.get('stock.location')
    >>> storage, = Location.find([
    ...         ('code', '=', 'STO'),
    ...         ])
    >>> inventory = Inventory()
    >>> inventory.location = storage
    >>> inventory_line = inventory.lines.new(product=product)
    >>> inventory_line.quantity = 100.0
    >>> inventory_line.expected_quantity = 0.0
    >>> inventory.click('confirm')
    >>> inventory.state
    'done'

Sale 5 products::

    >>> Sale = Model.get('sale.sale')
    >>> SaleLine = Model.get('sale.line')
    >>> sale = Sale()
    >>> sale.party = customer
    >>> sale.payment_term = payment_term
    >>> sale.paymode == paymode
    True
    >>> sale.paymode = paymode2
    >>> sale.invoice_method = 'order'
    >>> sale_line = SaleLine()
    >>> sale.lines.append(sale_line)
    >>> sale_line.product = product
    >>> sale_line.quantity = 2.0
    >>> sale_line = SaleLine()
    >>> sale.lines.append(sale_line)
    >>> sale_line.type = 'comment'
    >>> sale_line.description = 'Comment'
    >>> sale_line = SaleLine()
    >>> sale.lines.append(sale_line)
    >>> sale_line.product = product
    >>> sale_line.quantity = 3.0
    >>> sale.click('quote')
    >>> sale.untaxed_amount, sale.tax_amount, sale.total_amount
    (Decimal('50.00'), Decimal('5.00'), Decimal('55.00'))
    >>> sale.quoted_by == employee
    True
    >>> sale.click('confirm')
    >>> sale.untaxed_amount, sale.tax_amount, sale.total_amount
    (Decimal('50.00'), Decimal('5.00'), Decimal('55.00'))
    >>> sale.confirmed_by == employee
    True
    >>> sale.state
    'processing'
    >>> sale.shipment_state
    'waiting'
    >>> sale.invoice_state
    'pending'
    >>> len(sale.shipments), len(sale.shipment_returns), len(sale.invoices)
    (1, 0, 1)
    >>> invoice, = sale.invoices
    >>> invoice.origins == sale.rec_name
    True
    >>> shipment, = sale.shipments
    >>> shipment.origins == sale.rec_name
    True
    >>> invoice.paymode == paymode2
    True
