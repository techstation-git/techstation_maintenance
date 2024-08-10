// Copyright (c) 2020, Tech Station and contributors
// For license information, please see license.txt

frappe.ui.form.on('External Processing', {
    show_data: function (frm) {
        let d = new frappe.ui.Dialog({
            title: 'Select Payment Method',
            fields: [
                {
                    label: 'Payment Method',
                    fieldname: 'payment_method',
                    fieldtype: 'Link',
                    options: "Mode of Payment",
                    reqd: 1,
                    get_query() {

                        return {
                            filters: [
                                ["Mode of Payment", 'show_in_maintenance_for_payment', '=', 1]
                            ]
                        }
                    },
                },
                {
                    label: 'Warranty Template',
                    fieldname: 'warranty_template',
                    fieldtype: 'Link',
                    options: "Warranty Template",
                    default: frm.doc.warranty_template,
                    read_only: 1
                },
                {
                    label: 'Warranty Status',
                    fieldname: 'warranty_status',
                    fieldtype: 'Data',
                    default: frm.doc.warranty_status,
                    read_only: 1
                },
                // {
                // 	fieldname: 'sb_1',
                // 	fieldtype: 'Section Break'
                // },
                // {
                // 	label: 'Service Total',
                // 	fieldname: 's_total',
                // 	fieldtype: 'Currency',
                // 	default: frm.doc.service_total,
                // 	read_only: 1
                // },
                // {
                // 	fieldname: 'cb_1',
                // 	fieldtype: 'Column Break'
                // },
                // {
                // 	label: 'Service Net Total',
                // 	fieldname: 's_net_total',
                // 	fieldtype: 'Currency',
                // 	default: frm.doc.service_net_total,
                // 	read_only: 1
                // },
                // {
                // 	fieldname: 'sb_2',
                // 	fieldtype: 'Section Break'
                // },
                // {
                // 	label: 'Material Total',
                // 	fieldname: 'm_total',
                // 	fieldtype: 'Currency',
                // 	default: frm.doc.material,
                // 	read_only: 1
                // },
                // {
                // 	fieldname: 'cb_2',
                // 	fieldtype: 'Column Break'
                // },
                // {
                // 	label: 'Material Net Total',
                // 	fieldname: 'm_net_total',
                // 	fieldtype: 'Currency',
                // 	default: frm.doc.material_net_total,
                // 	read_only: 1
                // },
                // {
                // 	fieldname: 'sb_3',
                // 	fieldtype: 'Section Break'
                // },
                // {
                // 	label: 'Total Amount',
                // 	fieldname: 'total',
                // 	fieldtype: 'Currency',
                // 	default: frm.doc.grand_total,
                // 	read_only: 1
                // },
                // {
                // 	fieldname: 'cb_3',
                // 	fieldtype: 'Column Break'
                // },
                // {
                // 	label: 'Net Amount',
                // 	fieldname: 'net_total',
                // 	fieldtype: 'Currency',
                // 	default: frm.doc.net_grand_total,
                // 	read_only: 1
                // }
            ],
            primary_action_label: 'Submit',
            primary_action(values) {
                frm.set_value("payment_method", values.payment_method);
                console.log(values.payment_method)
                setTimeout(() => {
                    frm.trigger("make_maintenance_invoice");
                }, 5);

                d.hide();
            }
        });

        d.show();

    }
});

frappe.ui.form.on('External Processing', {
    refresh: function (frm) {
        if (frm.doc.docstatus == 1 && frm.doc.status != "Start" && frm.doc.status != "Rejected") {
            frm.add_custom_button(__("Start"), function () {
                frm.set_value("status", "Start");
                frm.save("Update");
            })
        }
        if (frm.doc.docstatus == 1 && (frm.doc.status == "Start" || frm.doc.status == "Delivered")) {
            frm.add_custom_button(__("Complete"), function () {
                frm.trigger("show_data");
            }).css({ "background-color": "#8bc34a", "color": "#000000" });
        }
        if (frm.doc.docstatus == 1 && frm.doc.status != "Rejected") {
            frm.add_custom_button(__("Reject"), function () {

                frappe.warn('Are you sure you want to proceed?',
                    'You Have to Confirm ?',
                    () => {
                        // action to perform if Continue is selected

                        frm.set_value("status", "Rejected")
                        frm.save("Update");
                        frm.trigger("update_all_document")
                    },
                    'Yes',
                    true // Sets dialog as minimizable
                )

            }).css({ "background-color": "coral", "color": "#000000" });
        }
    }
});

frappe.ui.form.on('External Processing', {
    make_maintenance_invoice: function (frm) {
        //		frm.save("Update");
        if (frm.doc.payment_method) {
            frappe.call({
                "method": "maintenance_system.maintenance_system.doctype.external_processing.external_processing.make_maintenance_invoice",
                args: {
                    doc: frm.doc.name,
                    mode: frm.doc.payment_method,
                },
                callback: function (r) {
                    frm.reload_doc()
                }
            });
        }
    },
    update_all_document: function (frm) {
        frappe.call({
            "method": "maintenance_system.maintenance_system.doctype.internal_processing.internal_processing.update_all_document",

            args: {
                doc: frm.doc.name,
                doctype: frm.doc.doctype,
                status: frm.doc.status
            },
            callback: function (r) {
            }
        });
    }
});


frappe.ui.form.on('External Processing', {
    refresh: function (frm) {
        var doc = frm.doc;
        if (doc.status == "Start" || doc.status == "Delivered") {
            frm.add_custom_button(__('Maintenance Material Receipt'),
                function () {
                    frm.trigger("make_maintenance_products_receipt")
                }, __('Create'));
        }
    },
    onload(frm) {
        frm.set_query("commission_benificiary", function () {
            return {
                "filters": {
                    "commission_enable": 1,
                }
            };
        });
    },
    make_maintenance_products_receipt: function () {
        frappe.model.open_mapped_doc({
            method: "maintenance_system.maintenance_system.doctype.external_processing.external_processing.make_maintenance_products_receipt",
            frm: cur_frm
        })
    }
});


frappe.ui.form.on('External Processing', {
    refresh: function (frm) {
        if (frm.doc.status == "Start" || frm.doc.status == "Delivered") {
            frm.remove_custom_button('Start');
        }
        if (frm.doc.status == "Complete" || frm.doc.status == "Unpaid" || frm.doc.status == "Paid" || frm.doc.status == "Rejected") {
            frm.remove_custom_button('Complete');
            frm.remove_custom_button('Start');
            frm.remove_custom_button('Reject');
            frm.set_df_property('services', 'read_only', 1);
        }
    }
});



frappe.ui.form.on("Maintenance Directing Service", "price", function (frm, cdt, cdn) {

    cur_frm.refresh_fields();
    var d = locals[cdt][cdn];
    var services = frm.doc.services;
    var total = 0
    for (var j in services) {
        total = total + services[j].price
        if (frm.doc.issue_date <= frm.doc.warranty_expiry_date && (frm.doc.warranty_type == "Service" || frm.doc.warranty_type == "Item and Service")) {
            frm.set_value("service_net_total", (total * (frm.doc.customer_tolerance / 100)));
            frm.set_value("service_total", total);
            frm.set_value("grand_total", total);
            frm.set_value("net_grand_total", frm.doc.service_net_total);

        }

        else {
            frm.set_value("service_total", total);
            frm.set_value("service_net_total", total);
            frm.set_value("grand_total", total);
            frm.set_value("net_grand_total", total);
        }

    }
});

frappe.ui.form.on("Maintenance Directing Service", "services_remove", function (frm, cdt, cdn) {

    cur_frm.refresh_fields();
    var d = locals[cdt][cdn];
    var services = frm.doc.services;
    var total = 0
    for (var j in services) {
        total = total + services[j].price
        if (frm.doc.issue_date <= frm.doc.warranty_expiry_date && (frm.doc.warranty_type == "Service" || frm.doc.warranty_type == "Item and Service")) {
            frm.set_value("service_net_total", (total * (frm.doc.customer_tolerance / 100)));
            frm.set_value("service_total", total);
            frm.set_value("grand_total", total);
            frm.set_value("net_grand_total", frm.doc.service_net_total);

        }

        else {
            frm.set_value("service_total", total);
            frm.set_value("service_net_total", total);
            frm.set_value("grand_total", total);
            frm.set_value("net_grand_total", total);
        }

    }
    cur_frm.refresh_fields();
    cur_frm.refresh();
});

frappe.ui.form.on('External Processing', {
    onload: function (frm) {
        frm.set_query("customer_address", function () {
            if (frm.doc.customer) {
                return {
                    query: 'frappe.contacts.doctype.address.address.address_query',
                    filters: {
                        link_doctype: "Customer",
                        link_name: frm.doc.customer
                    }
                };
            }
        })
        frm.set_query("contact", function () {
            if (frm.doc.customer) {
                return {
                    query: 'frappe.contacts.doctype.contact.contact.contact_query',
                    filters: {
                        link_doctype: "Customer",
                        link_name: frm.doc.customer
                    }
                };
            }
        })
    },

    customer: function (frm) {
        if (frm.doc.customer) {
            frm.events.set_address_name(frm, 'Customer', frm.doc.customer);
            frm.events.set_contact_name(frm, 'Customer', frm.doc.customer);
        }
        else {
            frm.set_value('customer_address', '');
            frm.set_value('address_display', '');
            frm.set_value('contact', '');
            frm.set_value('contact_display', '');
        }
    },
    set_address_name: function (frm, ref_doctype, ref_docname) {
        frappe.call({
            method: "maintenance_system.maintenance_system.doctype.maintenance_order.maintenance_order.get_address_name",
            args: {
                ref_doctype: ref_doctype,
                docname: ref_docname
            },
            callback: function (r) {
                if (r.message) {
                    frm.set_value('customer_address', r.message);
                }
            }
        });
    },
    set_contact_name: function (frm, ref_doctype, ref_docname) {
        frappe.call({
            method: "maintenance_system.maintenance_system.doctype.maintenance_order.maintenance_order.get_contact_name",
            args: {
                ref_doctype: ref_doctype,
                docname: ref_docname
            },
            callback: function (r) {
                if (r.message) {
                    frm.set_value('contact', r.message);
                }
            }
        });
    },
    customer_address: function (frm) {
        if (frm.doc.customer_address) {
            erpnext.utils.get_address_display(frm, 'customer_address', 'address_display', false);
        }
        if (!frm.doc.customer_address) {
            frm.set_value('address_display', '');
        }

    },
    contact: function (frm) {
        if (frm.doc.contact) {
            frm.events.get_contact_display(frm, frm.doc.contact);
        }
        if (!frm.doc.contact) {
            frm.set_value('contact_display', '');
        }
    },
    get_contact_display: function (frm, contact_name) {
        frappe.call({
            method: "frappe.contacts.doctype.contact.contact.get_contact_details",
            args: { contact: contact_name },
            callback: function (r) {
                if (r.message) {
                    let contact_display = r.message.contact_display;
                    if (r.message.contact_email) {
                        contact_display += '<br>' + r.message.contact_email;

                    }
                    if (r.message.contact_phone) {
                        contact_display += '<br>' + r.message.contact_phone;
                        frm.set_value('phone', r.message.contact_phone);
                    }
                    if (r.message.contact_mobile && !r.message.contact_phone) {
                        contact_display += '<br>' + r.message.contact_mobile;
                        frm.set_value('mobile_no', r.message.contact_mobile);
                    }
                    frm.set_value('contact_display', contact_display);
                } else {
                    frm.set_value('contact_display', '');
                }

            }
        });
    },
});






//External Processing Changes

//Update Delivery Date In All Row Item

frappe.ui.form.on("Maintenance Directing Spare Parts", {
    item_code: function (frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        if (frm.doc.delivery_date) {
            row.delivery_date = frm.doc.delivery_date;
            refresh_field("delivery_date", cdn, "table_68");
        } else {
            frm.script_manager.copy_from_first_row("table_68", row, ["delivery_date"]);
        }
    },
    delivery_date: function (frm, cdt, cdn) {
        if (!frm.doc.delivery_date) {
            erpnext.utils.copy_value_in_all_rows(frm.doc, cdt, cdn, "table_68", "delivery_date");
        }
    }
});

//Calculate Quantity and Amount For Service Items

frappe.ui.form.on("External Processing", {
    refresh: function (frm) {
        $(".grid-add-row").hide();
        $(".grid-remove-rows").hide();
    }
});

frappe.ui.form.on("Maintenance Directing Spare Parts", {
    item_code: function (frm, cdt, cdn) {


        var total = 0;
        var qty = 0;
        frm.doc.table_68.forEach(function (d) {
            frappe.db.get_value("Item Price", {
                "item_code": d.item_code, "price_list": frm.doc.price_list
            }, ['price_list_rate'], function (value) {
                if (typeof value.price_list_rate !== "undefined") {
                    total += value.price_list_rate * d.qty;
                    frm.set_value("spare_part_total", total);
                    var service_t = typeof frm.doc.service_total !== "undefined" ? frm.doc.service_total : 0;
                    frm.set_value("net_total", service_t + total)
                    var tax_t = typeof frm.doc.total_taxes_and_charges !== "undefined" ? frm.doc.total_taxes_and_charges : 0;
                    console.log(service_t + total + tax_t)
                    frm.set_value("grand_total", service_t + total + tax_t)
                }
            });
            qty += d.qty;
        });
        frm.set_value("total_quantity", qty);
        frm.set_value("spare_part_quantity", qty);
        refresh_field("spare_part_quantity");
        refresh_field("net_total");
        refresh_field("grand_total");
        refresh_field("total_quantity");
        refresh_field("spare_part_total");

    },
    qty: function (frm, cdt, cdn) {


        var total = 0;
        var qty = 0;
        frm.doc.table_68.forEach(function (d) {
            frappe.db.get_value("Item Price", {
                "item_code": d.item_code, "price_list": frm.doc.price_list
            }, ['price_list_rate'], function (value) {
                if (typeof value.price_list_rate !== "undefined") {
                    total += value.price_list_rate * d.qty;
                    frm.set_value("spare_part_total", total);
                    var service_t = typeof frm.doc.service_total !== "undefined" ? frm.doc.service_total : 0;
                    frm.set_value("net_total", service_t + total)
                    var tax_t = typeof frm.doc.total_taxes_and_charges !== "undefined" ? frm.doc.total_taxes_and_charges : 0;
                    console.log(service_t + total + tax_t)
                    frm.set_value("grand_total", service_t + total + tax_t)
                }
            });
            qty += d.qty;
        });
        frm.set_value("total_quantity", qty);
        frm.set_value("spare_part_quantity", qty);
        refresh_field("spare_part_quantity");
        refresh_field("net_total");
        refresh_field("grand_total");
        refresh_field("total_quantity");
        refresh_field("spare_part_total");

    },
    table_68_remove: function (frm, cdt, cdn) {
        var total = 0;
        var qty = 0;
        frm.doc.table_68.forEach(function (d) { total += d.amount; qty += d.qty; });
        frm.set_value("spare_part_total", total);
        frm.set_value("total_quantity", qty);
        frm.set_value("spare_part_quantity", qty);
        frm.set_value("net_total", frm.doc.service_total + total)
        var tax_t = typeof frm.doc.total_taxes_and_charges !== "undefined" ? frm.doc.total_taxes_and_charges : 0;
        // console.log(service_t+total+tax_t)
        frm.set_value("grand_total", frm.doc.service_total + total + tax_t)
        refresh_field("spare_part_quantity");
        refresh_field("net_total");
        refresh_field("grand_total");
        refresh_field("total_quantity");
        refresh_field("spare_part_total");

    }
});


//Calculate Quantity and Amount For Service Items

frappe.ui.form.on("Maintenance Directing Service", {
    maintenance_service: function (frm, cdt, cdn) {
        var total = 0;
        frm.doc.services.forEach(function (d) { total += d.price; });
        frm.set_value("service_total", total);
        var total_t = typeof frm.doc.spare_part_total !== "undefined" ? frm.doc.spare_part_total : 0;
        var tax_t = typeof frm.doc.total_taxes_and_charges !== "undefined" ? frm.doc.total_taxes_and_charges : 0;
        frm.set_value("net_total", total_t + total)
        frm.set_value("grand_total", total_t + total + tax_t)
        refresh_field("grand_total");
        refresh_field("net_total");
        refresh_field("service_total");

    },
    services_remove: function (frm, cdt, cdn) {
        var total = 0;
        frm.doc.services.forEach(function (d) { total += d.price; });
        frm.set_value("service_total", total);
        var total_t = typeof frm.doc.spare_part_total !== "undefined" ? frm.doc.spare_part_total : 0;
        var tax_t = typeof frm.doc.total_taxes_and_charges !== "undefined" ? frm.doc.total_taxes_and_charges : 0;
        frm.set_value("net_total", total_t + total)
        frm.set_value("grand_total", total_t + total + tax_t)
        refresh_field("grand_total");
        refresh_field("net_total");
        refresh_field("service_total");

    }
});

frappe.ui.form.on('External Processing', {
    make_maintenance_processing: function (frm) {
        frappe.call({
            "method": "maintenance_system.maintenance_system.doctype.maintenance_order.maintenance_order.make_maintenance_processing",
            args: {
                doc: frm.doc.name,
            },
            callback: function (r) {
            }
        });
    },
    onload(frm) {
        $(".grid-add-row").hide();
        if (!frm.doc.price_list && frm.doc.docstatus == 0) {
            frappe.model.with_doc("Maintenance System Settings", frm.doc.trigger, function () {
                var tabletransfer = frappe.model.get_doc("Maintenance System Settings");
                frm.set_value("price_list", tabletransfer.default_price_list)
                console.log(tabletransfer.default_price_list)
                cur_frm.refresh_field("price_list");
            });
        }

    },
    delivery_date: function (frm) {
        if (frm.doc.delivery_date < frappe.datetime.get_today()) {
            frm.set_value("delivery_date", "")
            frappe.throw("Delivery Date Should not Less than Current Date")
        }
        $.each(frm.doc.table_68 || [], function (i, d) {
            if (!d.delivery_date) d.delivery_date = frm.doc.delivery_date;
        });
        refresh_field("table_68");
    },
    before_save: function (frm) {
        if (frm.doc.grand_total && !frm.doc.payment_received) {
            frm.set_value("outstanding_amount", frm.doc.grand_total)
        }
        $.each(frm.doc.table_68 || [], function (i, d) {
            if (d.delivery_date < frappe.datetime.get_today()) {
                frappe.model.set_value(d.doctype, d.name, "delivery_date", "");
                frappe.throw("Delivery Date Should not Less than Current Date")
            }
            frm.doc.delivery_date = d.delivery_date
        });
    },
    total_taxes_and_charges: function (frm) {
        var total_t = typeof frm.doc.net_total !== "undefined" ? frm.doc.net_total : 0;
        var tax_t = typeof frm.doc.total_taxes_and_charges !== "undefined" ? frm.doc.total_taxes_and_charges : 0;
        console.log(total_t + tax_t)
        frm.set_value("grand_total", total_t + tax_t)
    }


});

//Filter For Item Color

// frappe.ui.form.on("Maintenance Order", "onload", function(frm) {
//     frm.set_query("item_color", function() {
//         return {
//             "filters": {
//                 "enable": 1,
//             }
//         };
//     });
// });
// //Filter For Item Model
// frappe.ui.form.on("Maintenance Order", "onload", function(frm) {
//     frm.set_query("item_model", function() {
//         return {
//             "filters": {
//                 "enable": 1,
//             }
//         };
//     });
// });
// //Filter For Item Status

// frappe.ui.form.on("Maintenance Order", "onload", function(frm) {
//     frm.set_query("item_status", function() {
//         return {
//             "filters": {
//                 "enable": 1,
//             }
//         };
//     });
// });


//Address Contact Filter







frappe.ui.form.on('Maintenance Directing Service', {
    refresh(frm, cdt, cdn) {
        var df = frappe.meta.get_docfield("Maintenance Order Items", "price", cur_frm.doc.name);
        df.hidden = 1;
    }
})


frappe.ui.form.on('Maintenance Directing Spare Parts', {
    item_code(frm, cdt, cdn) {
        var data = locals[cdt][cdn]
        frappe.db.get_value("Item Price", {
            "item_code": data.item_code,
        }, ['price_list_rate'], function (value) {
            if (typeof value.price_list_rate !== "undefined") {
                data.rate = value.price_list_rate
                data.amount = data.qty * value.price_list_rate
                refresh_field("table_70");
            }
        });
        refresh_field("table_70")
    },
    qty(frm, cdt, cdn) {
        var data = locals[cdt][cdn]
        data.amount = data.qty * data.rate
        refresh_field("table_70");
    }
})

//Calculate Taxes and Charges

frappe.ui.form.on("External Processing", "sales_taxes_and_charges_template", function (frm) {
    if (frm.doc.sales_taxes_and_charges_template) {
        var taxes = 0;
        var value = frm.doc.net_total;
        frappe.model.with_doc("Sales Taxes and Charges Template", frm.doc.sales_taxes_and_charges_template, function () {
            cur_frm.clear_table("tax");
            var tabletransfer = frappe.model.get_doc("Sales Taxes and Charges Template", frm.doc.sales_taxes_and_charges_template);
            $.each(tabletransfer.taxes, function (index, row) {
                var d = frm.add_child("tax");
                d.account_head = row.account_head;
                d.cost_center = row.cost_center;
                d.rate = row.rate;
                d.tax_amount = (row.rate / 100) * frm.doc.net_total;
                value = d.tax_amount + value;
                d.total = value;
                taxes = taxes + d.tax_amount;
                frm.set_value("total_taxes_and_charges", taxes);
                var service_t = typeof frm.doc.service_total !== "undefined" ? frm.doc.service_total : 0;
                if (typeof frm.doc.total !== "undefined") {
                    frm.set_value("grand_total", frm.doc.total + service_t + taxes)
                } else {
                    frm.set_value("grand_total", service_t + taxes)
                }
                refresh_field("grand_total");
                cur_frm.refresh_field("tax");
            });
        });
    }
    if (typeof (frm.doc.sales_taxes_and_charges_template) === "undefined" || typeof (frm.doc.sales_taxes_and_charges_template) === null || !frm.doc.sales_taxes_and_charges_template) {
        frm.set_value("total_taxes_and_charges", 0);
        refresh_field("total_taxes_and_charges");
        cur_frm.clear_table("tax");
        cur_frm.refresh_field("tax");

        var service_t = typeof frm.doc.service_total !== "undefined" ? frm.doc.service_total : 0;
        if (typeof frm.doc.total !== "undefined") {
            frm.set_value("grand_total", frm.doc.total + service_t + frm.doc.total_taxes_and_charges)
        } else {
            frm.set_value("grand_total", service_t + frm.doc.total_taxes_and_charges)
        }
        refresh_field("grand_total");
    }
});

frappe.ui.form.on("External Processing", "net_total", function (frm) {
    if (frm.doc.sales_taxes_and_charges_template) {
        var taxes = 0;
        var value = frm.doc.net_total;
        frappe.model.with_doc("Sales Taxes and Charges Template", frm.doc.sales_taxes_and_charges_template, function () {
            cur_frm.clear_table("tax");
            var tabletransfer = frappe.model.get_doc("Sales Taxes and Charges Template", frm.doc.sales_taxes_and_charges_template);
            $.each(tabletransfer.taxes, function (index, row) {
                var d = frm.add_child("tax");
                d.account_head = row.account_head;
                d.cost_center = row.cost_center;
                d.rate = row.rate;
                d.tax_amount = (row.rate / 100) * frm.doc.net_total;
                value = d.tax_amount + value;
                d.total = value;
                taxes = taxes + d.tax_amount;
                frm.set_value("total_taxes_and_charges", taxes);
                if (typeof frm.doc.total !== "undefined") {
                    frm.set_value("grand_total", frm.doc.total + frm.doc.service_total + taxes)
                } else {
                    frm.set_value("grand_total", frm.doc.service_total + taxes)
                }
                refresh_field("grand_total");
                cur_frm.refresh_field("tax");
            });
        });
    }
});
