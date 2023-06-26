frappe.listview_settings["GL Entry"] = {
	onload: function (listview) {
		listview.page.add_action_item(__("Update BS Reconcile Data"), function () {
			frappe.confirm(__("Update BS Reconcile Data"), () => {
				const gls = listview.get_checked_items();
				frappe.call({
					method: "bs_reconcile.overrides.gl_entry.update_bs_reconcile_data",
					freeze: true,
					args: {
						gls: gls,
					},
					callback: function () {
						listview.refresh();
					},
				});
			});
		});

		listview.page.add_action_item(__("Reconcile GL Entries"), function () {
			frappe.confirm(__("Reconcile GL Entries"), () => {
				const gls = listview.get_checked_items();
				frappe.call({
					method: "bs_reconcile.overrides.gl_entry.reconcile_gl_entries",
					freeze: true,
					args: {
						gls: gls,
					},
					callback: function () {
						listview.refresh();
					},
				});
			});
		});

		listview.page.add_action_item(__("Un-Reconcile GL Entries"), function () {
			frappe.confirm(__("Un-Reconcile GL Entries"), () => {
				const gls = listview.get_checked_items();
				frappe.call({
					method: "bs_reconcile.overrides.gl_entry.unreconcile_gl_entries",
					freeze: true,
					args: {
						gls: gls,
					},
					callback: function () {
						listview.refresh();
					},
				});
			});
		});
	},
};
