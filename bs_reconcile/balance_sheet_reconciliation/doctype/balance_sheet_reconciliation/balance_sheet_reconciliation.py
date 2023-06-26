# Copyright (c) 2023, FLO WORKS and contributors
# For license information, please see license.txt

import frappe
from frappe import _, msgprint, qb
from frappe.model.document import Document
from frappe.utils import flt, get_link_to_form, getdate, nowdate, today

from ...utils import reconcile_gl_entries


class BalanceSheetReconciliation(Document):
	@frappe.whitelist()
	def get_unreconciled_entries(self):
		self.check_mandatory_to_fetch()

		open_gl_entries = frappe.get_all(
			"GL Entry",
			fields=["*"],
			filters={
				"account": self.is_reconcile_account,
				"is_cancelled": 0,
				"is_reconcile": 1,
				"full_reconcile_number": "",
			},
		)
		all_entries = open_gl_entries.copy()

		if self.voucher_no or self.open_amount:
			open_gl_entries = []

		if self.voucher_no:
			open_gl_entries += list(
				filter(
					lambda x: self.voucher_no
					in (x.get("voucher_no") is None and "" or x.get("voucher_no"))
					or x["against_voucher"] is not None
					and self.voucher_no in x["against_voucher"],
					all_entries,
				)
			)

		if self.open_amount:
			open_gl_entries += list(
				filter(
					lambda x: abs(x["residual"]) == self.open_amount
					or abs(x["residual"]) == self.open_amount,
					all_entries,
				)
			)

		open_gl_entries = sorted(
			open_gl_entries, key=lambda k: k["posting_date"] or getdate(nowdate())
		)

		self.add_open_gl_entries(open_gl_entries)

	def check_mandatory_to_fetch(self):
		for fieldname in ["company", "is_reconcile_account"]:
			if not self.get(fieldname):
				frappe.throw(_("Please select {0} first").format(self.meta.get_label(fieldname)))

	def add_open_gl_entries(self, open_gl_entries):
		self.set("open_gl_entries", [])

		for gl in open_gl_entries:
			row = self.append("open_gl_entries", {})
			row.update(
				{
					"posting_date": gl.posting_date,
					"voucher_type": gl.voucher_type,
					"voucher_no": gl.voucher_no,
					"against": gl.against,
					"against_voucher_type": gl.against_voucher_type,
					"against_voucher_no": gl.against_voucher_no,
					"remarks": gl.remarks,
					"residual_debit": gl.residual > 0 and gl.residual or 0,
					"residual_credit": gl.residual < 0 and abs(gl.residual) or 0,
					"gl_entry": gl.name,
				}
			)

	@frappe.whitelist()
	def reconcile(self, args):
		selected_gl = args.get("gl_entries")
		if not len(selected_gl):
			msgprint(_("You have not select any record"))
			return
		debit = sum(x["residual_debit"] for x in selected_gl)
		credit = sum(x["residual_credit"] for x in selected_gl)
		if debit != credit:
			msgprint(_("Please make sure that open debit is equal to open credit"))
			return
		gl_ids = [x["gl_entry"] for x in selected_gl]
		gl_entries = frappe.get_all(
			"GL Entry", fields=["*"], filters={"name": ["in", gl_ids]}
		)
		reconcile_gl_entries(gl_entries)
		msgprint(_("Successfully Reconciled"))
