// Copyright (c) 2020, Tech Station and contributors
// For license information, please see license.txt


frappe.ui.form.on('Maintenance Material Receipt', {
    refresh: function (frm) {
        console.log('PRocess', frm.doc);
        if (frm.doc.docstatus == 1 && frm.doc.status == "Delivered") {
            frm.add_custom_button(__("Go To Processing"), function () {
                frappe.set_route("Form", frm.doc.processing_type, frm.doc.processing);
            })
        }
    }
});


frappe.ui.form.on("Maintenance Material Receipt", "customer", function (frm) {
    console.log('Cust', frm.doc);
    cur_frm.set_query("maintenance_processing", function () {
        return {
            "filters": {
                "customer": frm.doc.customer,
                "status": "Start"
            }
        };
    });
});


frappe.ui.form.on("Maintenance Material Receipt", "onload", function (frm) {
    console.log('MP', frm.doc);
    cur_frm.set_query("maintenance_processing", function () {
        return {
            "filters": {
                "customer": frm.doc.customer,
                "status": "Start"
            }
        };
    });
});



frappe.ui.form.on("Maintenance Material Receipt Table", {
    "item_code": function (frm, cdt, cdn) {
        var d2 = locals[cdt][cdn];
        if (d2.item_code) {
            frappe.call({
                "method": "maintenance_system.maintenance_system.doctype.maintenance_directing.maintenance_directing.getPrice",
                args: {
                    item_code: d2.item_code
                },
                callback: function (r) {
                    if (r.message) {
                        frappe.model.set_value(d2.doctype, d2.name, "rate", r.message[0][0]);
                        frappe.model.set_value(d2.doctype, d2.name, "uom", r.message[0][1]);
                    } else {
                        frappe.throw("Please Check Maintenance System Setting and Set Default Price List and Create an Item Price")
                    }
                }
            });
        }
    }
});



frappe.ui.form.on("Maintenance Material Receipt", {
    refresh: function (frm) {
        frm.trigger("onload")
    },
    onload: function (frm) {
        console.log('EXT', frm.doc);
        if (frm.doc.docstatus < 1 && !frm.doc.branch && frm.doc.processings) {
            frappe.call({
                "method": "maintenance_system.maintenance_system.doctype.maintenance_order.maintenance_order.order_default_branch",
                args: {
                    processing: frm.doc.processing,
                    doctype: frm.doc.processing_type.includes("EXT") ? "External Processing" : "Internal Processing"
                },
                callback: function (r) {
                    frm.set_value("branch", r.message)
                    cur_frm.save()
                }
            });
        }
    }
});



frappe.ui.form.on("Maintenance Material Receipt Table", "qty", function (frm, cdt, cdn) {

    var d = locals[cdt][cdn];
    frappe.model.set_value(d.doctype, d.name, "amount", d.qty * d.rate);
    var material = frm.doc.items;
    var total = 0
    for (var j in material) {
        total = total + material[j].amount
        frm.set_value("total", total);
    }
});

frappe.ui.form.on("Maintenance Material Receipt Table", "rate", function (frm, cdt, cdn) {
    var d = locals[cdt][cdn];
    frappe.model.set_value(d.doctype, d.name, "amount", d.qty * d.rate);
    var material = frm.doc.items;
    var total = 0
    for (var j in material) {
        total = total + material[j].amount
        frm.set_value("total", total);
    }
});

//Check Actual Quantity
frappe.ui.form.on("Maintenance Material Receipt", "warehouse", function (frm) {
    if (frm.doc.warehouse){
	    frm.doc.items.forEach(function (d) {
		frappe.call('maintenance_system.maintenance_system.doctype.maintenance_material_receipt.maintenance_material_receipt.update_actual', {
		    item_code: d.item_code, warehouse: frm.doc.warehouse
		}).then(r => {
		    frappe.model.set_value("Maintenance Material Receipt Table", d.name, "availability", r.message);

		})
	    });
	    cur_frm.refresh_fields("items");
    }
});

frappe.ui.form.on("Maintenance Material Receipt Table", "item_code", function (frm, cdt, cdn) {
    var d = locals[cdt][cdn];
    if (frm.doc.warehouse && d.item_code){	frappe.call('maintenance_system.maintenance_system.doctype.maintenance_material_receipt.maintenance_material_receipt.update_actual', {
		item_code: d.item_code, warehouse: frm.doc.warehouse
	    }).then(r => {
		frappe.model.set_value(cdt, cdn, "availability", r.message);
		cur_frm.refresh_fields("items");
	    })

    
    }
    
    
});



frappe.ui.form.on("Maintenance Material Receipt Table", "items_remove", function (frm, cdt, cdn) {

    var d = locals[cdt][cdn];
    var material = frm.doc.items;
    var total = 0
    for (var j in material) {
        total = total + material[j].amount
        frm.set_value("total", total);
    }
});

cur_frm.set_query("item_code", "items", function (doc, cdt, cdn) {
    var d = locals[cdt][cdn];
    return {
        filters: [
            ['Item', 'is_stock_item', '=', 1],
            ['Item', 'disabled', '=', 0],
            ['Item', 'is_sales_item', '=', 1]
        ]
    };
});

frappe.ui.form.on("Maintenance Material Receipt", "onload", function (frm) {
    if (frm.doc.docstatus < 1) {
        frm.set_value("delivery_date", frappe.datetime.get_today())
    }

});
frappe.ui.form.on("Maintenance Material Receipt", "edit_delivery_date", function (frm) {
    if (frm.doc.edit_delivery_date == 1) {
        frm.set_df_property("delivery_date", "read_only", 0)
    } else {
        frm.set_df_property("delivery_date", "read_only", 1)
    }
});
