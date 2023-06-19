
from bs_reconcile.balance_sheet_reconciliation.utils import get_gl_entries_by_vouchers
from bs_reconcile.balance_sheet_reconciliation.utils import reconcile_gl_entries


def bs_reconcile(doc, method):
    gl_entries = get_gl_entries_by_vouchers([doc.voucher_no, doc.against_voucher])
    reconcile_gl_entries(gl_entries)
