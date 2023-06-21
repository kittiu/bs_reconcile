import json
import frappe
from frappe import _, msgprint
from bs_reconcile.balance_sheet_reconciliation import utils


def bs_reconcile(doc, method):
    gl_entries = utils.get_gl_entries_by_vouchers([doc.voucher_no, doc.against_voucher])
    utils.reconcile_gl_entries(gl_entries)

@frappe.whitelist()
def update_bs_reconcile_data(gl_to_update):
    if isinstance(gl_to_update, str):
        gl_to_update = json.loads(gl_to_update)

    gl_list = [x["name"] for x in gl_to_update]
    for gl in gl_list:
        gl_entry = frappe.get_doc("GL Entry", gl)
        is_reconcile = frappe.get_cached_value("Account", gl_entry.account, "is_reconcile")
        gl_entry.is_reconcile = is_reconcile
        gl_entry.save()
        utils.update_gl_residual(gl_entry)
