// Copyright (c) 2020, Tech Station and contributors
// For license information, please see license.txt

frappe.ui.form.on('Receive Maintenance Item', {
	onload: function(frm) {
		frm.set_df_property('maintenance_malfunction',  'reqd',1);
	}
});

frappe.ui.form.on('Receive Maintenance Item', {
	refresh: function(frm) {
		var doc = frm.doc;
		if(doc.docstatus == 1 && doc.status == "Available") {
				frm.add_custom_button(__('Maintenance Order'),
                                        function() {
                                                frm.trigger("make_maintenance_order")
                                        }, __('Create'));
		}
},

	make_maintenance_order: function () {
                frappe.model.open_mapped_doc({
                        method: "maintenance_system.maintenance_system.doctype.receive_maintenance_item.receive_maintenance_item.make_maintenance_order",
                        frm: cur_frm
                })
        },
});


frappe.ui.form.on("Receive Maintenance Item", "maintenance_items", function(frm) {
    cur_frm.set_query("maintenance_item", function() {
        return {
            "filters": {
                "customer": frm.doc.customer,
		"docstatus": 1
                }
        };
    });
});


frappe.ui.form.on("Receive Maintenance Item", "onload", function(frm) {
    cur_frm.set_query("maintenance_item", function() {
        return {
            "filters": {
                "customer": frm.doc.customer,
		"docstatus": 1
                }
        };
    });
});


frappe.ui.form.on('Receive Maintenance Item', {
        customer: function(frm) {
                frm.set_value("maintenance_item","");
       }
});

cur_frm.set_query("malfunction", "maintenance_malfunction", function(doc, cdt, cdn) {
	var d = locals[cdt][cdn];
	return{
		filters: [
			['Maintenance Malfunction', 'enable', '=', 1]
		]
	};
});
