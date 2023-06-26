import json

import frappe
from frappe import _, msgprint

from bs_reconcile.balance_sheet_reconciliation import utils


def bs_reconcile(doc, method):
	gl_entries = utils.get_gl_entries_by_vouchers([doc.voucher_no, doc.against_voucher])
	utils.reconcile_gl_entries(gl_entries)


@frappe.whitelist()
def update_bs_reconcile_data(gls):
	if isinstance(gls, str):
		gls = json.loads(gls)

	gl_list = [x["name"] for x in gls]
	for gl in gl_list:
		gl_entry = frappe.get_doc("GL Entry", gl)
		is_reconcile = frappe.get_cached_value("Account", gl_entry.account, "is_reconcile")
		gl_entry.is_reconcile = is_reconcile
		gl_entry.save()
		utils.update_gl_residual(gl_entry)


def _get_gl_entries(gls):
	if isinstance(gls, str):
		gls = json.loads(gls)

	gl_list = [x["name"] for x in gls]
	gl_entries = frappe.get_all(
		"GL Entry", fields=["*"], filters={"name": ("in", gl_list)}
	)
	return gl_entries


@frappe.whitelist()
def reconcile_gl_entries(gls):
	utils.reconcile_gl(_get_gl_entries(gls))


@frappe.whitelist()
def unreconcile_gl_entries(gls):
	utils.unreconcile_gl(_get_gl_entries(gls))
