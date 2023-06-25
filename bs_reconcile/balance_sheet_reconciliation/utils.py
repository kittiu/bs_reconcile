import frappe
from frappe import _, qb
from frappe.query_builder.functions import Sum


def create_partial_reconcile_entries(gl_entries, allocated_amount=False):
	if allocated_amount: # From payment reconciliation
		if len(gl_entries) > 2:
			frappe.throw(_("Allocated amount is not allowed when reconcile more than 2 GL Entries"))
	for gl in gl_entries:
		update_gl_residual(gl)
	debit_entries = list(filter(lambda x: x.debit, gl_entries))
	credit_entries = list(filter(lambda x: x.credit, gl_entries))
	for dr in debit_entries:
		for cr in credit_entries:
			# Delete pre if already exists
			pre = qb.DocType("Partial Reconcile Entry")
			qb.from_(pre).delete().where(
				(pre.debit_gl_entry == dr.name) & (pre.credit_gl_entry == cr.name)
			).run()
			# Find amount to reconcile for this pre
			amount = min(dr.debit, cr.credit, abs(dr.residual), abs(cr.residual))
			if allocated_amount:
				amount = min(amount, allocated_amount)
			doc = dict(
				doctype="Partial Reconcile Entry",
				debit_gl_entry=dr.name,
				credit_gl_entry=cr.name,
				amount=amount
			)
			pre = frappe.get_doc(doc)
			pre.insert(ignore_permissions=True)
			update_gl_residual(dr)
			update_gl_residual(cr)

def get_all_related_gl_entries(gl_list):
	prev_gl_list = gl_list.copy()
	pre_debit_entries = frappe.db.get_all(
		"Partial Reconcile Entry",
		fields=["name", "debit_gl_entry"],
		filters=[dict(credit_gl_entry=("in", gl_list))],
	)
	gl_list += [x["debit_gl_entry"] for x in pre_debit_entries]
	pre_credit_entries = frappe.db.get_all(
		"Partial Reconcile Entry",
		fields=["name", "credit_gl_entry"],
		filters=[dict(debit_gl_entry=("in", gl_list))],
	)
	gl_list += [x["credit_gl_entry"] for x in pre_credit_entries]
	gl_list = list(set(gl_list))
	if len(prev_gl_list) < len(gl_list):
		get_all_related_gl_entries(gl_list)
	pre_list = [x["name"] for x in pre_debit_entries + pre_credit_entries]
	return (gl_list, pre_list)

def get_gl_entries_by_vouchers(vouchers, is_cancelled=0):
	gl_entries = frappe.db.get_all(
		"GL Entry",
		fields=["*"],
		filters=[
			dict(is_cancelled=("=", is_cancelled)),
			dict(is_reconcile=("=", 1)),
			dict(voucher_no=("in", vouchers)),
		],
		order_by="posting_date asc",
	)
	return gl_entries

def mark_full_reconcile(gl_to_reconcile):
	# Recursive scan to get all related gl from partial reconcile entries
	gl_list = list([x.name for x in gl_to_reconcile])
	gl_list, pre_list = get_all_related_gl_entries(gl_list)
	# If all residual are zero we can mark them as Full Reconciled
	glt = qb.DocType("GL Entry")
	residual = (
		qb.from_(glt).select((Sum(glt.residual)).as_("residual"))
		.where((glt.name.isin(gl_list))).run()
	)
	if not residual[0][0]:
		fre = frappe.get_doc(dict(doctype="Full Reconcile Number")).save()
		for gl in gl_list:
			frappe.db.set_value("GL Entry", gl, "full_reconcile_number", fre.name)
		for pre in pre_list:
			frappe.db.set_value("Partial Reconcile Entry", pre, "full_reconcile_number", fre.name)

def reconcile_gl_entries(gl_entries, allocated_amount=False):
	"""
	Reconcile gl_entries, but first try to match voucher and against voucher first
	If not matching, fall back to reconcile_gl()
	"""
	# Validation
	for gl in gl_entries:
		if not gl.is_reconcile:
			frappe.throw(_("GL Entry {0} / Account {1} can not reconcile").format(gl.name, gl.account, ))
	# gl with against voucher, we can match clearer and clearee gl before reconcile
	gl_clearer = list(filter(
		lambda x: x.get("against_voucher") and x.get("against_voucher") != x.get("voucher_no"),
		gl_entries
	))
	# gl_entries = list(set(gl_entries).difference(set(gl_clearer)))
	gl_entries = list([x for x in gl_entries if x not in gl_clearer])
	for glc in gl_clearer:
		gl_clearee = list(filter(
			lambda x: x.get("voucher_no") == glc.get("against_voucher"),
			gl_entries
		))
		gl_entries = list([x for x in gl_entries if x not in gl_clearee])
		gl_to_reconcile = [glc] + gl_clearee
		reconcile_gl(gl_to_reconcile, allocated_amount=allocated_amount)
	# other gl w/o against voucher, just reconcile as a single group
	reconcile_gl(gl_entries, allocated_amount=allocated_amount)

def reconcile_gl(gl_to_reconcile, allocated_amount=False):
	"""
	Main method to reconcile any input gl entreis
	"""
	accounts = list(set([x.account for x in gl_to_reconcile]))
	for a in accounts:
		gl_entries = list(filter(lambda x: x.account == a, gl_to_reconcile))
		create_partial_reconcile_entries(gl_entries, allocated_amount)
		# If all residuals are zero, mark as fully reconciled
		if set([x.residual for x in gl_entries]) == {0}:
			mark_full_reconcile(gl_entries)

def unreconcile_gl(gl_to_unreconcile):
	# remove full reconcile number everywhere
	gl_list = [x["name"] for x in gl_to_unreconcile]
	gl_list, pre_list = get_all_related_gl_entries(gl_list)
	# Unset full_reconcile_number for GL Entry and Partial Reconcile Entry
	if gl_list:
		tab = qb.DocType("GL Entry")
		qb.update(tab).set(tab.full_reconcile_number, None).where(
			(tab.name.isin(gl_list))
		).run()
	if pre_list:
		tab = qb.DocType("Partial Reconcile Entry")
		qb.update(tab).set(tab.full_reconcile_number, None).where(
			(tab.name.isin(pre_list))
		).run()

	# Delete related partial reconcie entries
	gl_list = [x.name for x in gl_to_unreconcile]
	pre_list = frappe.get_all(
		"Partial Reconcile Entry",
		fields=["*"],
		filters=[dict(debit_gl_entry=("in", gl_list))],
		or_filters=[dict(credit_gl_entry=("in", gl_list))],
	)
	if pre_list:
		tab = qb.DocType("Partial Reconcile Entry")
		qb.from_(tab).delete().where(
			tab.name.isin([x.name for x in pre_list])
		).run()
	# Finally, update the gl residual again
	for pre in pre_list:
		update_gl_residual(frappe.get_doc("GL Entry", pre.debit_gl_entry))
		update_gl_residual(frappe.get_doc("GL Entry", pre.credit_gl_entry))

def update_gl_residual(gl):
	if not gl.is_reconcile:
		return
	if gl.is_cancelled:
		frappe.db.set_value("GL Entry", gl.name, "residual", 0)
		return
	# Begin amount
	gl_amount = gl.debit - gl.credit
	# Used amount
	pre = qb.DocType("Partial Reconcile Entry")
	debit = (
		qb.from_(pre).select((Sum(pre.amount)).as_("total_debit"))
		.where((pre.debit_gl_entry == gl.name)).run()
	)
	credit = (
		qb.from_(pre).select((Sum(pre.amount)).as_("total_credit"))
		.where((pre.credit_gl_entry == gl.name)).run()
	)
	reconciled_amount = (debit[0][0] or 0) - (credit[0][0] or 0)
	# Update Residual
	gl.residual = gl_amount - reconciled_amount
	frappe.db.set_value("GL Entry", gl.name, "residual", gl.residual)
