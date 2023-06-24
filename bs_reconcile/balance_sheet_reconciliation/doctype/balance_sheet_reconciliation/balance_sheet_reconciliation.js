// Copyright (c) 2023, FLO WORKS and contributors
// For license information, please see license.txt
frappe.ui.form.on('Balance Sheet Reconciliation', {

	onload(frm) {
		const default_company = frappe.defaults.get_default('company');
		frm.set_value('company', default_company);
		frm.set_value('is_reconcile_account', '');

		frm.set_query("is_reconcile_account", () => {
			return {
				"filters": {
					"is_reconcile": true,
				}
			}
		});
	},

	refresh(frm) {
		frm.disable_save();

		frm.set_df_property('open_gl_entries', 'cannot_delete_rows', true);
		frm.set_df_property('open_gl_entries', 'cannot_add_rows', true);

		if (frm.doc.is_reconcile_account) {
			frm.add_custom_button(__('Get Unreconciled Entries'), () =>
				frm.trigger("get_unreconciled_entries")
			);
			frm.change_custom_button_type('Get Unreconciled Entries', null, 'primary');
		}

		if (frm.doc.open_gl_entries.length) {
			frm.add_custom_button(__('Reconcile'), () =>
				frm.trigger("reconcile_gl_entries")
			);
			frm.change_custom_button_type('Reconcile', null, 'primary');
			frm.change_custom_button_type('Get Unreconciled Entries', null, 'default');
		}

        frm.fields_dict.open_gl_entries.grid.wrapper.on('click', '.grid-row', function(event) {
			let gl_entries = frm.fields_dict.open_gl_entries.grid.get_selected_children()
			const sum_debit = gl_entries.reduce((accumulator, object) => {
				return accumulator + object.residual_debit;
			}, 0);
			const sum_credit = gl_entries.reduce((accumulator, object) => {
				return accumulator + object.residual_credit;
			}, 0);
			frm.set_value('sum_debit', sum_debit);
			frm.set_value('sum_credit', sum_credit);
		});
	},

	company(frm) {
		frm.set_value('is_reconcile_account', '');
	},

	is_reconcile_account(frm) {
		frm.trigger("clear_child_tables");
		frm.refresh();
	},

	get_unreconciled_entries(frm) {
		return frm.call({
			doc: frm.doc,
			method: 'get_unreconciled_entries',
			callback: () => {
				frm.refresh();
			}
		});
	},

	clear_child_tables(frm) {
		frm.clear_table("open_gl_entries");
		frm.refresh_fields();
	},

	reconcile_gl_entries(frm) {
		let gl_entries = frm.fields_dict.open_gl_entries.grid.get_selected_children();
		return frm.call({
			doc: frm.doc,
			method: 'reconcile',
			args: {
				gl_entries: gl_entries
			},
			callback: () => {
				frm.clear_table("open_gl_entries");
				frm.trigger("get_unreconciled_entries")
			}
		});
	},
})
