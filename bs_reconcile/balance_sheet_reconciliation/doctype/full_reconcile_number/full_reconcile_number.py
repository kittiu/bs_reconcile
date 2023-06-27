# Copyright (c) 2023, FLO WORKS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class FullReconcileNumber(Document):
	def on_trash(self):
		docs = frappe.get_list(
			"Partial Reconcile Entry", filters={"full_reconcile_number": self.name}, pluck="name"
		)
		for doc in docs:
			frappe.delete_doc_if_exists("Partial Reconcile Entry", doc)
