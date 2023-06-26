# Copyright (c) 2023, FLO WORKS and Contributors
# See license.txt
import frappe
from frappe.utils import now

from bs_reconcile.balance_sheet_reconciliation.utils import (
    get_gl_entries_by_vouchers, unreconcile_gl)


def set_as_cancel(voucher_type, voucher_no):
	"""
	Set is_cancelled=1 in all original gl entries for the voucher
	"""
	frappe.db.sql(
		"""UPDATE `tabGL Entry` SET is_cancelled = 1,
        modified=%s, modified_by=%s
        where voucher_type=%s and voucher_no=%s and is_cancelled = 0""",
		(now(), frappe.session.user, voucher_type, voucher_no),
	)

	# Patch
	gl_to_unreconcile = get_gl_entries_by_vouchers([voucher_no], is_cancelled=1)
	unreconcile_gl(gl_to_unreconcile)
	# --
