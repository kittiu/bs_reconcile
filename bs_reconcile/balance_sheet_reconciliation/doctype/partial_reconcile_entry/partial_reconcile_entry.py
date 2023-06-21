# Copyright (c) 2023, FLO WORKS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from bs_reconcile.balance_sheet_reconciliation import utils

class PartialReconcileEntry(Document):
	
	def after_delete(self):
		gl_entries = frappe.get_all(
			"GL Entry",
			fields=["*"],
			filters={"name": ("in", [self.debit_gl_entry, self.credit_gl_entry])}
		)
		utils.unreconcile_gl(gl_entries)
		for gl in gl_entries:
			utils.update_gl_residual(gl)

