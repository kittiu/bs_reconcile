import frappe
from erpnext.accounts.doctype.payment_reconciliation.payment_reconciliation import PaymentReconciliation
from bs_reconcile.balance_sheet_reconciliation.utils import get_gl_entries_by_vouchers
from bs_reconcile.balance_sheet_reconciliation.utils import reconcile_gl_entries

class BSPaymentReconciliation(PaymentReconciliation):
	
    @frappe.whitelist()
    def reconcile(self):
        super(self).reconcile()
        # Patch reconcile
        for a in self.allocation:
            gl_entries = get_gl_entries_by_vouchers([a.reference_name, a.invoice_number])
            reconcile_gl_entries(gl_entries, allocated_amount=a.allocated_amount)
		# --
