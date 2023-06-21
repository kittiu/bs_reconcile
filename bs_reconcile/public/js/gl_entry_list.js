frappe.listview_settings['GL Entry'] = {
	onload: function(listview) {
        listview.page.add_action_item(__('Update BS Reconcile Data'), function() {
            frappe.confirm(__('Update BS Reconcile Data'), () => {
                const gl_to_update = listview.get_checked_items();
                frappe.call({
                    method: 'bs_reconcile.overrides.gl_entry.update_bs_reconcile_data',
                    freeze: true,
                    args: {
                        'gl_to_update': gl_to_update
                    }
                });
            })
        });
	}
};
