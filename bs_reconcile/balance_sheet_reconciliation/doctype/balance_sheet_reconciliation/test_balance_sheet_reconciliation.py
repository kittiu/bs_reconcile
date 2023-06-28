# Copyright (c) 2023, FLO WORKS and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import today

from bs_reconcile.balance_sheet_reconciliation.utils import (
    get_gl_entries_by_vouchers, reconcile_gl_entries)


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
		Full reconcile simple 1 AR and 1 AP with equal amount = 100
		"""
		# Create PI with amount 100
		pi = make_purchase_invoice(rate=100)
		residual, full_reconciled = get_reconcile_status(pi)
		self.assertEqual(residual, -100)
		self.assertFalse(full_reconciled)
		# Create PE with amount 100
		pe = make_payment_entry(amount=100)
		residual, full_reconciled = get_reconcile_status(pe)
		self.assertEqual(residual, 100)
		self.assertFalse(full_reconciled)
		# Reconcile creditors
		gl_entries = get_gl_entries_by_vouchers([pi.name, pe.name])
		reconcile_gl_entries(gl_entries)
		# Test that residuals become zero
		residual, full_reconciled = get_reconcile_status(pi)
		self.assertEqual(residual, 0)
		self.assertTrue(full_reconciled)
		residual, full_reconciled = get_reconcile_status(pe)
		self.assertEqual(residual, 0)
		self.assertTrue(full_reconciled)

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
		# Test invoice status
		residual, full_reconciled = get_reconcile_status(pi)
		self.assertEqual(residual, -60)
		self.assertFalse(full_reconciled)
		# Test payment status
		residual, full_reconciled = get_reconcile_status(pe)
		self.assertEqual(residual, 0)
		self.assertFalse(full_reconciled)
		# Create PE with amount 60
		pe = make_payment_entry(amount=60)
		# 2nd Reconcile (Full)
		gl_entries = get_gl_entries_by_vouchers([pi.name, pe.name])
		reconcile_gl_entries(gl_entries)
		# Test 2nd invoice status
		residual, full_reconciled = get_reconcile_status(pi)
		self.assertEqual(residual, 0)
		self.assertTrue(full_reconciled)
		# Test payment status
		residual, full_reconciled = get_reconcile_status(pe)
		self.assertEqual(residual, 0)
		self.assertTrue(full_reconciled)

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
		gl_entries = get_gl_entries_by_vouchers(
			[pi_1.name, pi_2.name, pi_3.name, pi_4.name, pe_1.name, pe_2.name]
		)
		reconcile_gl_entries(gl_entries)
		# Test all documents should have fully reconiled
		for doc in [pi_1, pi_2, pi_3, pe_1, pe_2]:
			residual, full_reconciled = get_reconcile_status(doc)
			self.assertEqual(residual, 0)
			self.assertTrue(full_reconciled)

	def test_auto_reconcile_invoice_payment(self):
		"""
		Auto reconcile if payment is done against invoice(s)
		Test with 2 invoice and 1 payment
		"""
		pi_1 = make_purchase_invoice(rate=100)
		pi_2 = make_purchase_invoice(rate=200)
		pe = make_payment_entry(amount=300, do_not_submit=True)
		pi_ref_1 = {
			"reference_doctype": pi_1.doctype,
			"reference_name": pi_1.name,
			"allocated_amount": 100,
		}
		pi_ref_2 = {
			"reference_doctype": pi_2.doctype,
			"reference_name": pi_2.name,
			"allocated_amount": 200,
		}
		pe.append("references", pi_ref_1)
		pe.append("references", pi_ref_2)
		pe.save()
		pe.submit()
		# Test all documents should have fully reconiled
		for doc in [pi_1, pi_2, pe]:
			residual, full_reconciled = get_reconcile_status(doc)
			self.assertEqual(residual, 0)
			self.assertTrue(full_reconciled)

	def test_cancel_voucher_to_unreconcile(self):
		"""
		Auto reconcile if payment is done against invoice(s)
		Test with 2 invoice and 1 payment
		"""
		pi = make_purchase_invoice(rate=100)
		pe = make_payment_entry(amount=100, do_not_submit=True)
		pi_ref = {
			"reference_doctype": pi.doctype,
			"reference_name": pi.name,
			"allocated_amount": 100,
		}
		pe.append("references", pi_ref)
		pe.save()
		pe.submit()
		# Test all documents should have fully reconiled
		for doc in [pi, pe]:
			residual, full_reconciled = get_reconcile_status(doc)
			self.assertEqual(residual, 0)
			self.assertTrue(full_reconciled)
		# Cancel payment, all should be unreconciled
		pe.cancel()
		# Invoice, back to unreconciled
		residual, full_reconciled = get_reconcile_status(pi)
		self.assertEqual(residual, -100)
		self.assertFalse(full_reconciled)
		# Payment, cancelled, so no residual also
		residual, full_reconciled = get_reconcile_status(pe)
		self.assertEqual(residual, 0)
		self.assertFalse(full_reconciled)

	def test_delete_partial_reoncile_entry_to_unreconcile(self):
		# Create PI with amount 100
		pi = make_purchase_invoice(rate=100)
		# Create PE with amount 100
		pe = make_payment_entry(amount=100)
		# Reconcile creditors
		gl_entries = get_gl_entries_by_vouchers([pi.name, pe.name])
		reconcile_gl_entries(gl_entries)
		# Test that residuals become zero
		residual, full_reconciled = get_reconcile_status(pi)
		self.assertEqual(residual, 0)
		self.assertTrue(full_reconciled)
		residual, full_reconciled = get_reconcile_status(pe)
		self.assertEqual(residual, 0)
		self.assertTrue(full_reconciled)
		# Now, delete the partial reconcile entry, and test again.
		pre = frappe.get_all(
			"Partial Reconcile Entry",
			filters={"debit_voucher": pe.name, "credit_voucher": pi.name},
			pluck="name",
		)
		frappe.get_doc("Partial Reconcile Entry", pre[0]).delete()
		# They will be like never been reconciled
		residual, full_reconciled = get_reconcile_status(pi)
		self.assertEqual(residual, -100)
		self.assertFalse(full_reconciled)
		residual, full_reconciled = get_reconcile_status(pe)
		self.assertEqual(residual, 100)
		self.assertFalse(full_reconciled)

	def test_delete_full_reoncile_entry_to_unreconcile(self):
		# Create PI with amount 100
		pi = make_purchase_invoice(rate=100)
		# Create PE with amount 100
		pe = make_payment_entry(amount=100)
		# Reconcile creditors
		gl_entries = get_gl_entries_by_vouchers([pi.name, pe.name])
		reconcile_gl_entries(gl_entries)
		# Test that residuals become zero
		residual, full_reconciled = get_reconcile_status(pi)
		self.assertEqual(residual, 0)
		self.assertTrue(full_reconciled)
		residual, full_reconciled = get_reconcile_status(pe)
		self.assertEqual(residual, 0)
		self.assertTrue(full_reconciled)
		# Now, delete the full reconcile number, and test again.
		frappe.get_doc("Full Reconcile Number", full_reconciled).delete()
		# They will be like never been reconciled
		residual, full_reconciled = get_reconcile_status(pi)
		self.assertEqual(residual, -100)
		self.assertFalse(full_reconciled)
		residual, full_reconciled = get_reconcile_status(pe)
		self.assertEqual(residual, 100)
		self.assertFalse(full_reconciled)


def make_purchase_invoice(**args):
	pi = frappe.new_doc("Purchase Invoice")
	args = frappe._dict(args)
	pi.posting_date = today()
	pi.company = args.company or "_Test Company"
	pi.supplier = args.supplier or "_Test Supplier"  # Creditors - _TC
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


def get_reconcile_status(voucher):
	gl_entries = frappe.db.sql(
		"""select sum(residual) as residual, min(full_reconcile_number) as reconciled 
		from `tabGL Entry`
		where voucher_type=%s and voucher_no=%s""",
		(
			voucher.doctype,
			voucher.name,
		),
		as_dict=1,
	)
	return (gl_entries[0]["residual"], gl_entries[0]["reconciled"])
