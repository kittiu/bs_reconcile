frappe.ui.form.on('GL Entry', {

    update_bs_reconcile_data: function(frm) {
        frappe.confirm(__('Update BS Reconcile Data'), () => {
            frappe.call({
                method: 'bs_reconcile.overrides.gl_entry.update_bs_reconcile_data',
                freeze: true,
                args: {
                    'gl_to_update': [{'name': frm.docname}]
                }
            });
        })
    },

})
