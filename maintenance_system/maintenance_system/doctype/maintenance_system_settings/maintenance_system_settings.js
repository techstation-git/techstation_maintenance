// Copyright (c) 2020, Tech Station and contributors
// For license information, please see license.txt

frappe.ui.form.on('Maintenance System Settings', {
	 receive_payment_mode: function(frm) {
		frm.set_value("account","");
	 }
});

frappe.ui.form.on("Maintenance System Settings", "receive_payment_mode", function(frm) {
    cur_frm.set_query("account", function() {
        return {
            "filters": {
		"is_group": 0,
                "account_type": ["in", "Cash, Bank"]
                }
        };
    });
});

frappe.ui.form.on("Maintenance System Settings", "onload", function(frm) {
    cur_frm.set_query("account", function() {
        return {
            "filters": {
		"is_group": 0,
                "account_type": ["in", "Cash, Bank"]
                }
        };
    });
});

frappe.ui.form.on("Maintenance System Settings", "onload", function(frm) {
    cur_frm.set_query("cost_center", function() {
        return {
            "filters": {
                "is_group": 0
                }
        };
    });
});

frappe.ui.form.on("Maintenance System Settings", "onload", function(frm) {
    cur_frm.set_query("debtors_account", function() {
        return {
            "filters": {
                "is_group": 0,
                "account_type": "Receivable"
                }
        };
    });
});
