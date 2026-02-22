frappe.ui.form.on('Maintenance Service Report', {
    setup: function (frm) {
        if (frm.is_new()) {
            frm.set_value('service_date', frappe.datetime.get_today());
            frm.set_value('service_time', frappe.datetime.get_time());
        }
    },
    refresh: function (frm) {
        // Possible enhancement: add button to open the linked Maintenance Order
    }
});
