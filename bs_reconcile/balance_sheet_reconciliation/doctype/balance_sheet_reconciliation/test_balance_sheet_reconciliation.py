# Copyright (c) 2023, FLO WORKS and Contributors
# See license.txt

import frappe
from frappe.utils import today
from frappe.tests.utils import FrappeTestCase
from bs_reconcile.balance_sheet_reconciliation.utils import reconcile_gl_entries
from bs_reconcile.balance_sheet_reconciliation.utils import get_gl_entries_by_vouchers


class TestBalanceSheetReconciliation(FrappeTestCase):
	def setUp(self):
		# Setup testing account
		frappe.set_value("Account", "Creditors - _TC", "is_reconcile", 1)
		# Change user to accounts user
		frappe.get_doc("User", "test@example.com").add_roles("Accounts User")
		frappe.set_user("test@example.com")

	def tearDown(self):
		frappe.set_user("Administrator")
	
	def test_simple_full_reconcile(self):
		"""
		Fulle reconcile simple 1 AR and 1 AP with equal amount = 100
		"""
		# Create PI with amount 100
		pi = make_purchase_invoice(rate=100)
		# Check GLE for Purchase Invoice
		expected_gle = [
			["_Test Account Cost for Goods Sold - _TC", 100, 0, 0, False],
			["Creditors - _TC", 0, 100, -100, False],
		]
		check_gl_entries(self, pi, expected_gle)
		# Create PE with amount 100
		pe = make_payment_entry(amount=100)
		expected_gle = [
			["Cash - _TC", 0, 100, 0, False],
			["Creditors - _TC", 100, 0, 100, False],
		]
		check_gl_entries(self, pe, expected_gle)
		# Reconcile creditors
		gl_entries = get_gl_entries_by_vouchers([pi.name, pe.name])
		reconcile_gl_entries(gl_entries)
		# Test that residuals become zero
		expected_gle = [
			["_Test Account Cost for Goods Sold - _TC", 100, 0, 0, False],
			["Creditors - _TC", 0, 100, 0, True],
		]
		check_gl_entries(self, pi, expected_gle)
		expected_gle = [
			["Cash - _TC", 0, 100, 0, False],
			["Creditors - _TC", 100, 0, 0, True],
		]
		check_gl_entries(self, pe, expected_gle)

	def test_simple_partial_reconcile_to_full(self):
		"""
		Reconcile simple 1 AR and 1 AP with equal amount = 100
		"""
		# Create PI with amount 100
		pi = make_purchase_invoice(rate=100)
		# Create PE with amount 40
		pe = make_payment_entry(amount=40)
		# 1st Reconcile
		gl_entries = get_gl_entries_by_vouchers([pi.name, pe.name])
		reconcile_gl_entries(gl_entries)
		expected_gle = [
			["_Test Account Cost for Goods Sold - _TC", 100, 0, 0, False],
			["Creditors - _TC", 0, 100, -60, False],
		]
		check_gl_entries(self, pi, expected_gle)
		expected_gle = [
			["Cash - _TC", 0, 40, 0, False],
			["Creditors - _TC", 40, 0, 0, False],
		]
		check_gl_entries(self, pe, expected_gle)
		# Create PE with amount 60
		pe = make_payment_entry(amount=60)
		# 2nd Reconcile (Full)
		gl_entries = get_gl_entries_by_vouchers([pi.name, pe.name])
		reconcile_gl_entries(gl_entries)
		expected_gle = [
			["_Test Account Cost for Goods Sold - _TC", 100, 0, 0, False],
			["Creditors - _TC", 0, 100, 0, True],
		]
		check_gl_entries(self, pi, expected_gle)
		expected_gle = [
			["Cash - _TC", 0, 60, 0, False],
			["Creditors - _TC", 60, 0, 0, True],
		]
		check_gl_entries(self, pe, expected_gle)

	def test_complex_partial_to_full_reconcile(self):
		"""
		Reconcile Invoice 30, 20, 10, 40 with Payment = 10, 90
		"""
		pi_1 = make_purchase_invoice(rate=30)
		pi_2 = make_purchase_invoice(rate=20)
		pi_3 = make_purchase_invoice(rate=10)
		pi_4 = make_purchase_invoice(rate=40)
		pe_1 = make_payment_entry(amount=10)
		pe_2 = make_payment_entry(amount=90)
		gl_entries = get_gl_entries_by_vouchers([
			pi_1.name, pi_2.name, pi_3.name, pi_4.name,
			pe_1.name, pe_2.name
		])
		reconcile_gl_entries(gl_entries)
		# Test with pi_3, and p2_2, both should have fully reconiled
		expected_gle = [
			["_Test Account Cost for Goods Sold - _TC", 10, 0, 0, False],
			["Creditors - _TC", 0, 10, 0, True],
		]
		check_gl_entries(self, pi_3, expected_gle)
		expected_gle = [
			["Cash - _TC", 0, 90, 0, False],
			["Creditors - _TC", 90, 0, 0, True],
		]
		check_gl_entries(self, pe_2, expected_gle)

	# def test_payment_reconciliation_to_reconcile(self):
	# 	pass
	
	# def test_auto_reconcile_invoice_payment(self):
	# 	pass

	# def test_cancel_voucher_to_unreconcile(self):
	# 	pass

	# def test_delete_partial_reoncile_entry_to_unreconcile(self):
	# 	pass


def make_purchase_invoice(**args):
	pi = frappe.new_doc("Purchase Invoice")
	args = frappe._dict(args)
	pi.posting_date = today()
	pi.company = args.company or "_Test Company"
	pi.supplier = args.supplier or "_Test Supplier" # Creditors - _TC
	pi.currency = "INR"
	pi.append(
		"items",
		{
			"item_name": args.item or args.item_code or "_Test Item",
			"qty": args.qty or 1,
			"rate": args.rate or 100,
			"expense_account": args.expense_account or "_Test Account Cost for Goods Sold - _TC",
			"cost_center": args.cost_center or "_Test Cost Center - _TC",
		},
	)
	pi.insert()
	if not args.do_not_submit:
		pi.submit()
	return pi

def make_payment_entry(**args):
	pe = frappe.new_doc("Payment Entry")
	args = frappe._dict(args)
	pe.posting_date = today()
	pe.company = args.company or "_Test Company"
	pe.paid_from_account_currency = "INR"
	pe.paid_to_account_currency = "INR"
	pe.source_exchange_rate = 1
	pe.target_exchange_rate = 1
	pe.payment_type = "Pay"
	pe.mode_of_payment = "Cash"
	pe.paid_from = "Cash - _TC"
	pe.party_type = "Supplier"
	pe.party = "_Test Supplier"
	pe.paid_amount = args.amount or 100
	pe.received_amount = -args.amount or -100
	if not args.do_not_submit:
		pe.submit()
	return pe


def check_gl_entries(doc, voucher, expected_gle,):
	gl_entries = frappe.db.sql(
		"""select account, debit, credit, residual, full_reconcile_number
		from `tabGL Entry`
		where voucher_type=%s and voucher_no=%s
		order by posting_date asc, account asc""",
		(voucher.doctype, voucher.name,),
		as_dict=1,
	)
	doc.assertTrue(gl_entries)
	for i, gle in enumerate(gl_entries):
		doc.assertEqual(expected_gle[i][0], gle.account)
		doc.assertEqual(expected_gle[i][1], gle.debit)
		doc.assertEqual(expected_gle[i][2], gle.credit)
		doc.assertEqual(expected_gle[i][3], gle.residual)
		if expected_gle[i][4]:
			doc.assertTrue(gle.full_reconcile_number)
		else:
			doc.assertFalse(gle.full_reconcile_number)
