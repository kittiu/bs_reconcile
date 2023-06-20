// Copyright (c) 2023, FLO WORKS and contributors
// For license information, please see license.txt
frappe.provide("bs_reconcile");
bs_reconcile.BSReconcileController = class BSReconcileController extends frappe.ui.form.Controller {

	onload() {
		const default_company = frappe.defaults.get_default('company');
		this.frm.set_value('company', default_company);
		this.frm.set_value('is_reconcile_account', '');

		this.frm.set_query("is_reconcile_account", () => {
			return {
				"filters": {
					"is_reconcile": true,
				}
			}
		});
	}

	refresh() {
		this.frm.disable_save();
		this.frm.set_df_property('open_gl_entries', 'cannot_delete_rows', true);
		this.frm.set_df_property('open_gl_entries', 'cannot_add_rows', true);

		if (this.frm.doc.is_reconcile_account) {
			this.frm.add_custom_button(__('Get Unreconciled Entries'), () =>
				this.frm.trigger("get_unreconciled_entries")
			);
			this.frm.change_custom_button_type('Get Unreconciled Entries', null, 'primary');
		}
		console.log(this.frm.doc.open_gl_entries)
		if (this.frm.doc.open_gl_entries.length) {
			this.frm.add_custom_button(__('Reconcile'), () =>
				this.frm.trigger("reconcile_gl_entries")
			);
			this.frm.change_custom_button_type('Reconcile', null, 'primary');
			this.frm.change_custom_button_type('Get Unreconciled Entries', null, 'default');
		}
	}

	company() {
		this.frm.set_value('is_reconcile_account', '');
	}

	is_reconcile_account() {
		this.frm.trigger("clear_child_tables");
		this.frm.refresh();
	}

	get_unreconciled_entries() {
		return this.frm.call({
			doc: this.frm.doc,
			method: 'get_unreconciled_entries',
			callback: () => {
				if (!(this.frm.doc.open_gl_entries.length)) {
					frappe.throw({message: __("No Unreconciled gl entries found for this account")});
				}
				this.frm.refresh();
			}
		});

	}

	clear_child_tables() {
		this.frm.clear_table("open_gl_entries");
		this.frm.refresh_fields();
	}

	reconcile_gl_entries() {
		let gl_entries = this.frm.fields_dict.open_gl_entries.grid.get_selected_children();
		return this.frm.call({
			doc: this.frm.doc,
			method: 'reconcile',
			args: {
				gl_entries: gl_entries
			},
			callback: () => {
				this.frm.clear_table("open_gl_entries");
				this.frm.refresh();
			}
		});
	}

};

extend_cscript(cur_frm.cscript, new bs_reconcile.BSReconcileController({frm: cur_frm}));


// frappe.provide("erpnext.accounts");
// erpnext.accounts.PaymentReconciliationController = class PaymentReconciliationController extends frappe.ui.form.Controller {
// 	onload() {
// 		const default_company = frappe.defaults.get_default('company');
// 		this.frm.set_value('company', default_company);

// 		this.frm.set_value('party_type', '');
// 		this.frm.set_value('party', '');
// 		this.frm.set_value('receivable_payable_account', '');

// 		this.frm.set_query("party_type", () => {
// 			return {
// 				"filters": {
// 					"name": ["in", Object.keys(frappe.boot.party_account_types)],
// 				}
// 			}
// 		});

// 		this.frm.set_query('receivable_payable_account', () => {
// 			return {
// 				filters: {
// 					"company": this.frm.doc.company,
// 					"is_group": 0,
// 					"account_type": frappe.boot.party_account_types[this.frm.doc.party_type]
// 				}
// 			};
// 		});

// 		this.frm.set_query('bank_cash_account', () => {
// 			return {
// 				filters:[
// 					['Account', 'company', '=', this.frm.doc.company],
// 					['Account', 'is_group', '=', 0],
// 					['Account', 'account_type', 'in', ['Bank', 'Cash']]
// 				]
// 			};
// 		});

// 		this.frm.set_query("cost_center", () => {
// 			return {
// 				"filters": {
// 					"company": this.frm.doc.company,
// 					"is_group": 0
// 				}
// 			}
// 		});
// 	}

// 	refresh() {
// 		this.frm.disable_save();

// 		this.frm.set_df_property('invoices', 'cannot_delete_rows', true);


