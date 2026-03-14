// Copyright (c) 2020, Tech Station and contributors
// For license information, please see license.txt

// 104446975824192
cur_frm.set_query("malfunction", "maintenance_malfunctions", function (doc, cdt, cdn) {
    var d = locals[cdt][cdn];
    return {
        filters: [
            ['Maintenance Malfunction', 'enable', '=', 1]
        ]
    };
});

frappe.ui.form.on('Maintenance Order', {
    validate: function (frm) {
        if (frm.doc.warranty_start_date && frm.doc.warranty_period) {
            var date = new Date(frm.doc.warranty_start_date);
            date.setDate(date.getDate() + frm.doc.warranty_period);
            var ndate = date.getDate();
            var nm = date.getMonth() + 1;
            var ny = date.getFullYear();
            var date1 = ny + "-" + nm + "-" + ndate;
            frm.set_value("warranty_expiry_date", date1);
        }

    },
    refresh: function (frm) {
        refresh_field("maintenance_malfunctions")
        refresh_field("table_60")
    },
    onload(frm) {
        refresh_field("table_60")
        if (frm.doc.docstatus < 1) {
            frm.set_query("commission_benificiary", function () {
                return {
                    "filters": {
                        "commission_enable": 1,
                    }
                };
            });
        }

    }
});


frappe.ui.form.on('Maintenance Order', 'customer', function (frm) {
    frm.set_value("receive_maintenance_items", "");
    frm.set_value("maintenance_item", "");
});


frappe.ui.form.on('Maintenance Order', 'delivery_type', function (frm) {
    if (frm.doc.delivery_type == "Received") {
        // frm.set_df_property('receive_maintenance_items',  'reqd',1);
    }
    if (frm.doc.delivery_type != "Received") {
        frm.set_df_property('receive_maintenance_items', 'reqd', 0);
    }
});



frappe.ui.form.on('Maintenance Order', 'onload', function (frm) {
    if (frm.doc.receive_maintenance_items && frm.doc.docstatus < 1) {
        frm.set_value("order_type", "Internal");
        frm.set_value("delivery_type", "Received");
    }
});


frappe.ui.form.on("Maintenance Order", {
    get_advance_payment: function (frm) {
        if (frm.doc.get_advance_payment == 1) {
            cur_frm.refresh();
            cur_frm.clear_table("maintenance_advance_payment");
            cur_frm.refresh_fields();

            frappe.call({
                "method": "maintenance_system.maintenance_system.doctype.maintenance_order.maintenance_order.getPE",
                args: {
                    party: frm.doc.customer
                },
                callback: function (r) {
                    var len = r.message.length;
                    for (var i = 0; i < len; i++) {
                        var row = frm.add_child("maintenance_advance_payment");
                        row.payment_entry = r.message[i][0];
                        row.mode = r.message[i][1];
                        row.date = r.message[i][2];
                        row.amount = r.message[i][3];
                    }
                    cur_frm.refresh();
                }
            });
        }
        if (frm.doc.get_advance_payment == 0) {
            cur_frm.refresh();
            cur_frm.clear_table("maintenance_advance_payment");
        }
    }
});

frappe.ui.form.on("Maintenance Order", "delivery_type", function (frm) {
    cur_frm.set_query("receive_maintenance_items", function () {
        return {
            "filters": {
                "status": "Available",
                "customer": frm.doc.customer
            }
        };
    });
});

frappe.ui.form.on("Maintenance Order", "onload", function (frm) {
    if (frm.doc.docstatus < 1) {
        cur_frm.set_query("receive_maintenance_items", function () {
            return {
                "filters": {
                    "status": "Available",
                    "customer": frm.doc.customer
                }
            };
        });
    }
});

frappe.ui.form.on("Maintenance Order", "receive_maintenance_items", function (frm) {
    if (frm.doc.receive_maintenance_items) {
        cur_frm.set_query("maintenance_item", function () {
            return {
                "filters": {
                    "customer": frm.doc.customer,
                    "receive_maintenance_item": frm.doc.receive_maintenance_items,
                    "docstatus": 1
                }
            };
        });
    }
});

frappe.ui.form.on("Maintenance Order", "onload", function (frm) {
    if (frm.doc.receive_maintenance_items && frm.doc.docstatus < 1) {
        cur_frm.set_query("maintenance_item", function () {
            return {
                "filters": {
                    "customer": frm.doc.customer,
                    "receive_maintenance_item": frm.doc.receive_maintenance_items,
                    "docstatus": 1
                }
            };
        });
    }
});


frappe.ui.form.on("Maintenance Order", "onload", function (frm) {
    if (!frm.doc.receive_maintenance_items) {
        cur_frm.set_query("maintenance_item", function () {
            return {
                "filters": {
                    "customer": frm.doc.customer,
                    "docstatus": 1
                }
            };
        });
    }
});


frappe.ui.form.on("Maintenance Order", "receive_maintenance_items", function (frm) {
    if (frm.doc.receive_maintenance_items) {
        frappe.model.with_doc("Receive Maintenance Item", frm.doc.receive_maintenance_items, function () {
            cur_frm.clear_table("maintenance_malfunction_item");
            var tabletransfer = frappe.model.get_doc("Receive Maintenance Item", frm.doc.receive_maintenance_items);
            $.each(tabletransfer.maintenance_malfunction, function (index, row) {
                var d = frm.add_child("maintenance_malfunction_item");
                d.malfunction = row.malfunction;
                frm.set_value("accessories", tabletransfer.accessories);
                cur_frm.refresh_field("maintenance_malfunction_item");
            });
        });
    }
});


frappe.ui.form.on('Maintenance Order', {
    territory: function (frm) {
        if (frm.doc.order_type == "External" && frm.doc.territory) {
            frm.set_value("maintenance_schedule", "External");
            frappe.call({
                "method": "maintenance_system.maintenance_system.doctype.maintenance_order.maintenance_order.getDate",
                args: {
                    order_type: frm.doc.maintenance_schedule,
                    territory: frm.doc.territory
                },
                callback: function (r) {
                    var date = new Date(frm.doc.issue_date);
                    date.setDate(date.getDate() + r.message[0][0]);
                    var ndate = date.getDate();
                    var nm = date.getMonth() + 1;
                    var ny = date.getFullYear();
                    var date1 = ny + "-" + nm + "-" + ndate;
                    frm.set_value("maintenance_end_date", date1);
                }
            });
        }
    },
    order_type: function (frm) {
        if (frm.doc.order_type == "Internal") {
            frm.set_value("maintenance_schedule", "Internal");
            frappe.call({
                "method": "maintenance_system.maintenance_system.doctype.maintenance_order.maintenance_order.getIntrnalDate",
                args: {
                    order_type: frm.doc.maintenance_schedule
                },
                callback: function (r) {
                    var date = new Date(frm.doc.issue_date);
                    date.setDate(date.getDate() + r.message[0][0]);
                    var ndate = date.getDate();
                    var nm = date.getMonth() + 1;
                    var ny = date.getFullYear();
                    var date1 = ny + "-" + nm + "-" + ndate;
                    frm.set_value("maintenance_end_date", date1);
                    frm.refresh_field("maintenance_end_date")
                }
            });
        }
        if (frm.doc.order_type == "External" && frm.doc.territory) {
            frm.set_value("maintenance_schedule", "External");
            frappe.call({
                "method": "maintenance_system.maintenance_system.doctype.maintenance_order.maintenance_order.getDate",
                args: {
                    order_type: frm.doc.maintenance_schedule,
                    territory: frm.doc.territory
                },
                callback: function (r) {
                    var date = new Date(frm.doc.issue_date);
                    date.setDate(date.getDate() + r.message[0][0]);
                    var ndate = date.getDate();
                    var nm = date.getMonth() + 1;
                    var ny = date.getFullYear();
                    var date1 = ny + "-" + nm + "-" + ndate;
                    frm.set_value("maintenance_end_date", date1);
                    frm.refresh_field("maintenance_end_date")
                }
            });
        }

    }
});


frappe.ui.form.on('Maintenance Order', {
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
                {
                    fieldname: 'sb_1',
                    fieldtype: 'Section Break'
                },
                {
                    fieldname: 'sb_3',
                    fieldtype: 'Section Break'
                },
                {
                    label: 'Total Amount',
                    fieldname: 'total',
                    fieldtype: 'Currency',
                    default: frm.doc.total_amount,
                    read_only: 1
                },
                {
                    fieldname: 'cb_3',
                    fieldtype: 'Column Break'
                },
                {
                    label: 'Net Amount',
                    fieldname: 'net_total',
                    fieldtype: 'Currency',
                    default: frm.doc.total_amount,
                    read_only: 1
                }
            ],
            primary_action_label: 'Submit',
            primary_action(values) {
                frm.set_value("payment_method", values.payment_method);
                frm.trigger("make_maintenance_payment")
                d.hide();
            }
        });

        d.show();

    },
    make_maintenance_payment: function (frm) {
        frappe.call({
            "method": "maintenance_system.maintenance_system.doctype.maintenance_invoice.maintenance_invoice.make_payment_entry",
            args: {
                doc: frm.doc.name,
                mode: frm.doc.payment_method,
                doctype: "Maintenance Order",
                docname: frm.doc.name,
                posting_date: frm.doc.issue_date
            },
            callback: function (r) {
                frm.reload_doc()
            }
        });
    },
    refresh: function (frm) {
        if (frm.doc.docstatus == 1) {

            frm.add_custom_button(__("Barcode"), function () {
                window.open("/printview?doctype=Maintenance%20Order&name=" + frm.doc.name + "&trigger_print=1&format=Barcode%20Printing&no_letterhead=1&letterhead=No%20Letterhead&settings=%7B%7D&_lang=en-US")
            }).css({ 'backgroudcolor': 'black', 'font-weight': 'bold' });

            frm.add_custom_button(__("POS Receipt"), function () {
                window.open("/printview?doctype=Maintenance%20Order&name=" + frm.doc.name + "&trigger_print=1&format=POS Receipt Maintenance Order&no_letterhead=1&letterhead=No Letterhead&settings={}&_lang=en-US")
            }).css({ 'backgroudcolor': 'black', 'font-weight': 'bold' });

            cur_frm.page.set_inner_btn_group_as_primary(__('Create'));

            frm.add_custom_button(__("Directing"), function () {
                frappe.set_route("Form", "Maintenance Directing", frm.doc.maintenance_directing);
            }, __("Go To"));
            frm.add_custom_button(__("Maintenance Item"), function () {
                frappe.set_route("Form", "Maintenance Item", frm.doc.maintenance_item);
            }, __("Go To"));
            frm.add_custom_button(__("Warranty Template"), function () {
                frappe.set_route("Form", "Warranty Template", frm.doc.warranty_template);
            }, __("Go To"));
        }
        if (frm.doc.docstatus == 1 && frm.doc.status == "Waiting") {
            frm.add_custom_button(__("Maintenance Directing"), function () {
                frm.trigger("make_maintenance_processing")
            }, ("Create"))
        }
        if (frm.doc.docstatus == 1 && !frm.doc.maintenance_payment) {
            frm.add_custom_button(__("Payment"), function () {
                frm.trigger("show_data");
            }, ("Create"))
        }

        if (frm.doc.docstatus == 1 && frm.doc.status == "In Processing") {
            frm.add_custom_button(__("Issue Custody"), function () {
                frm.trigger("make_technician_custody");
            }, __("Create"));

            frm.add_custom_button(__("Service Report"), function () {
                frappe.new_doc("Maintenance Service Report", {
                    maintenance_order: frm.doc.name,
                    customer: frm.doc.customer
                });
            }, __("Create"));
        }

        if (frm.doc.docstatus == 1) {
            frm.add_custom_button(__("Technician Custody"), function () {
                frappe.set_route("List", "Technician Custody", { maintenance_order: frm.doc.name });
            }, __("Go To"));
        }
    },
    make_technician_custody: function (frm) {
        let d = new frappe.ui.Dialog({
            title: __("Issue Custody"),
            fields: [
                {
                    label: __("Technician"),
                    fieldname: "employee",
                    fieldtype: "Link",
                    options: "Employee",
                    reqd: 1
                },
                {
                    label: __("Original Warehouse"),
                    fieldname: "original_warehouse",
                    fieldtype: "Link",
                    options: "Warehouse",
                    reqd: 1
                }
            ],
            primary_action_label: __("Proceed"),
            primary_action(values) {
                frappe.model.with_doctype("Technician Custody", function () {
                    let new_doc = frappe.model.get_new_doc("Technician Custody");
                    new_doc.maintenance_order = frm.doc.name;
                    new_doc.employee = values.employee;
                    new_doc.original_warehouse = values.original_warehouse;

                    // Optional: Pull items from Maintenance Order child tables if needed, 
                    // or just open the form for manual entry.
                    // For now, let's just open the form with initial values.

                    frappe.set_route("Form", "Technician Custody", new_doc.name);
                });
                d.hide();
            }
        });
        d.show();
    },
    branch: function (frm) {
        refresh_field("table_60")
        frm.trigger("onload")
    },
    onload: function (frm) {
        frm.set_query("maintenance_team", function () {
            return {
                "filters": {
                    "branch": (frm.doc.branch) ? frm.doc.branch : " ",
                    "enable": 1
                }
            };
        });
        frm.set_query("branch", function () {
            return {
                "filters": {
                    "enable": 1
                }
            };
        });
        if (frm.doc.docstatus < 1) {
            frappe.call({
                "method": "maintenance_system.maintenance_system.doctype.maintenance_order.maintenance_order.default_branch",
                callback: function (r) {
                    frm.set_value("branch", r.message)
                }
            });
        }

        if (!frm.doc.delivery_date && frm.doc.docstatus < 1) {
            frm.set_value("delivery_date", frappe.datetime.get_today())
        }

    }

});


//Update Delivery Date In All Row Item

frappe.ui.form.on("Maintenance Order Spare Parts", {
    item_code: function (frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        if (frm.doc.delivery_date) {
            row.delivery_date = frm.doc.delivery_date;
            refresh_field("delivery_date", cdn, "table_66");
        } else {
            frm.script_manager.copy_from_first_row("table_66", row, ["delivery_date"]);
        }
    },
    delivery_date: function (frm, cdt, cdn) {
        if (!frm.doc.delivery_date) {
            erpnext.utils.copy_value_in_all_rows(frm.doc, cdt, cdn, "table_66", "delivery_date");
        }
    }
});

//Calculate Quantity and Amount For Service Items

frappe.ui.form.on("Maintenance Order Spare Parts", {
    item_code: function (frm, cdt, cdn) {


        var total = 0;
        var qty = 0;
        frm.doc.table_66.forEach(function (d) {
            frappe.db.get_value("Item Price", {
                "item_code": d.item_code, "price_list": frm.doc.price_list
            }, ['price_list_rate'], function (value) {
                if (typeof value.price_list_rate !== "undefined") {
                    total += value.price_list_rate * d.qty;
                    frm.set_value("total", total);
                    var service_t = typeof frm.doc.service_total !== "undefined" ? frm.doc.service_total : 0;
                    frm.set_value("net_total", service_t + total)
                    var tax_t = typeof frm.doc.total_taxes_and_charges !== "undefined" ? frm.doc.total_taxes_and_charges : 0;
                    frm.set_value("total_amount", service_t + total + tax_t)
                }
            });
            qty += d.qty;
        });
        frm.set_value("total_quantity", qty);
        frm.set_value("net_quantity", qty);
        refresh_field("net_quantity");
        refresh_field("net_total");
        refresh_field("total_amount");
        refresh_field("total_quantity");
        refresh_field("total");

    },
    qty: function (frm, cdt, cdn) {


        var total = 0;
        var qty = 0;
        frm.doc.table_66.forEach(function (d) {
            frappe.db.get_value("Item Price", {
                "item_code": d.item_code, "price_list": frm.doc.price_list
            }, ['price_list_rate'], function (value) {
                if (typeof value.price_list_rate !== "undefined") {
                    total += value.price_list_rate * d.qty;
                    frm.set_value("total", total);
                    var service_t = typeof frm.doc.service_total !== "undefined" ? frm.doc.service_total : 0;
                    frm.set_value("net_total", service_t + total)
                    var tax_t = typeof frm.doc.total_taxes_and_charges !== "undefined" ? frm.doc.total_taxes_and_charges : 0;
                    frm.set_value("total_amount", service_t + total + tax_t)
                }
            });
            qty += d.qty;
        });
        frm.set_value("total_quantity", qty);
        frm.set_value("net_quantity", qty);
        refresh_field("net_quantity");
        refresh_field("net_total");
        refresh_field("total_amount");
        refresh_field("total_quantity");
        refresh_field("total");

    },
    table_66_remove: function (frm, cdt, cdn) {
        var total = 0;
        var qty = 0;
        frm.doc.table_66.forEach(function (d) { total += d.amount; qty += d.qty; });
        frm.set_value("total", total);
        frm.set_value("total_quantity", qty);
        frm.set_value("net_quantity", qty);
        frm.set_value("net_total", frm.doc.service_total + total)
        var tax_t = typeof frm.doc.total_taxes_and_charges !== "undefined" ? frm.doc.total_taxes_and_charges : 0;
        frm.set_value("total_amount", service_t + total + tax_t)
        refresh_field("net_quantity");
        refresh_field("net_total");
        refresh_field("total_amount");
        refresh_field("total_quantity");
        refresh_field("total");

    }
});


//Calculate Quantity and Amount For Service Items

frappe.ui.form.on("Maintenance Order Items", {
    maintenance_service: function (frm, cdt, cdn) {
        var total = 0;
        frm.doc.table_60.forEach(function (d) { total += d.price; });
        frm.set_value("service_total", total);
        var total_t = typeof frm.doc.total !== "undefined" ? frm.doc.total : 0;
        var tax_t = typeof frm.doc.total_taxes_and_charges !== "undefined" ? frm.doc.total_taxes_and_charges : 0;
        frm.set_value("net_total", total_t + total)
        frm.set_value("total_amount", total_t + total + tax_t)
        refresh_field("total_amount");
        refresh_field("net_total");
        refresh_field("service_total");
        frm.trigger('calculate_rewards');

    },
    table_60_remove: function (frm, cdt, cdn) {
        var total = 0;
        frm.doc.table_60.forEach(function (d) { total += d.price; });
        frm.set_value("service_total", total);
        var total_t = typeof frm.doc.total !== "undefined" ? frm.doc.total : 0;
        var tax_t = typeof frm.doc.total_taxes_and_charges !== "undefined" ? frm.doc.total_taxes_and_charges : 0;
        frm.set_value("net_total", total_t + total)
        frm.set_value("total_amount", total_t + total + tax_t)
        refresh_field("total_amount");
        refresh_field("net_total");
        refresh_field("service_total");

    }
});

frappe.ui.form.on('Maintenance Order', {
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
        if (!frm.doc.price_list && frm.doc.docstatus < 1) {
            frappe.model.with_doc("Maintenance System Settings", frm.doc.trigger, function () {
                var tabletransfer = frappe.model.get_doc("Maintenance System Settings");
                frm.set_value("price_list", tabletransfer.default_price_list)
                cur_frm.refresh_field("price_list");
                frm.set_value("company", tabletransfer.company)

                if (tabletransfer.company) {
                    frappe.call({
                        method: "maintenance_system.maintenance_system.doctype.maintenance_order.maintenance_order.get_company_address",
                        args: {
                            company: tabletransfer.company
                        },
                        callback: function (r) {
                            frm.set_value("company_address", r.message)

                        }
                    });
                }
                if (!frm.doc.sales_taxes_and_charges_template && tabletransfer.tax_required && tabletransfer.sales_taxes_and_charges_template) {
                    frm.set_value("sales_taxes_and_charges_template", tabletransfer.sales_taxes_and_charges_template)
                    cur_frm.refresh_field("sales_taxes_and_charges_template");
                }

            });
        }

    },
    delivery_date: function (frm) {
        if (frm.doc.delivery_date < frappe.datetime.get_today()) {
            frm.set_value("delivery_date", "")
            frappe.throw("Delivery Date Should not Less than Current Date")
        }
        $.each(frm.doc.table_66 || [], function (i, d) {
            if (!d.delivery_date) d.delivery_date = frm.doc.delivery_date;
        });
        refresh_field("table_66");
    },
    before_save: function (frm) {
        if (frm.doc.total_amount && !frm.doc.payment_received) {
            frm.set_value("outstanding_amount", frm.doc.total_amount)
        }
        $.each(frm.doc.table_66 || [], function (i, d) {
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
        frm.set_value("total_amount", total_t + tax_t)
    }


});

//Filter For Item Color

frappe.ui.form.on("Maintenance Order", "onload", function (frm) {
    frm.set_query("item_color", function () {
        return {
            "filters": {
                "enable": 1,
            }
        };
    });
});
//Filter For Item Model
frappe.ui.form.on("Maintenance Order", "onload", function (frm) {
    frm.set_query("item_model", function () {
        return {
            "filters": {
                "enable": 1,
            }
        };
    });
});
//Filter For Item Status

frappe.ui.form.on("Maintenance Order", "onload", function (frm) {
    frm.set_query("item_status", function () {
        return {
            "filters": {
                "enable": 1,
            }
        };
    });
});


//Address Contact Filter




frappe.ui.form.on('Maintenance Order', {
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


frappe.ui.form.on('Maintenance Order Items', {
    refresh(frm, cdt, cdn) {
        var df = frappe.meta.get_docfield("Maintenance Order Items", "price", cur_frm.doc.name);
        df.hidden = 1;
    }
})


frappe.ui.form.on('Maintenance Order Spare Parts', {
    item_code(frm, cdt, cdn) {
        if (frm.doc.price_list) {
            var data = locals[cdt][cdn]
            frappe.db.get_value("Item Price", {
                "item_code": data.item_code, "price_list": frm.doc.price_list
            }, ['price_list_rate'], function (value) {
                if (typeof value.price_list_rate !== "undefined") {
                    data.rate = value.price_list_rate
                    data.amount = data.qty * value.price_list_rate
                    refresh_field("table_66");
                } else {
                    frappe.throw("Prease Create a Item Price For " + frm.doc.price_list + " Price List")
                }
            });
            refresh_field("table_66")
        } else {
            frappe.throw("Prease Select a Default Price List in Maintenance System Settings" + frm.doc.price_list)
        }


    },
    qty(frm, cdt, cdn) {
        var data = locals[cdt][cdn]
        data.amount = data.qty * data.rate
        refresh_field("table_66");
    }
})

//Calculate Taxes and Charges

frappe.ui.form.on("Maintenance Order", "sales_taxes_and_charges_template", function (frm) {
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
                    frm.set_value("total_amount", frm.doc.total + service_t + taxes)
                } else {
                    frm.set_value("total_amount", service_t + taxes)
                }
                refresh_field("total_amount");
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
            frm.set_value("total_amount", frm.doc.total + service_t + frm.doc.total_taxes_and_charges)
        } else {
            frm.set_value("total_amount", service_t + frm.doc.total_taxes_and_charges)
        }
        refresh_field("total_amount");
    }
});

frappe.ui.form.on("Maintenance Order", "net_total", function (frm) {
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
                    frm.set_value("total_amount", frm.doc.total + frm.doc.service_total + taxes)
                } else {
                    frm.set_value("total_amount", frm.doc.service_total + taxes)
                }
                refresh_field("total_amount");
                cur_frm.refresh_field("tax");
            });
        });
    }
});

frappe.ui.form.on('Maintenance Order', {
    refresh: function (frm) {
        if (frm.doc.docstatus == 1 && frm.doc.status == "Complete") {
            if (frappe.user_roles.includes("Operations Officer")) {
                frm.toggle_enable("maintenance_assignments", true);
                // Also need to set fields as editable in the grid
                frm.fields_dict.maintenance_assignments.grid.editable_status = true;
            } else {
                frm.toggle_enable("maintenance_assignments", false);
            }
        }
    },
    calculate_rewards: function (frm) {
        var total_amount = frm.doc.total_amount || 0;
        var material_total = frm.doc.total || 0;
        var commissionable_amount = total_amount - material_total;

        $.each(frm.doc.maintenance_assignments || [], function (i, d) {
            if (d.reward_mode === 'Labor Percentage') {
                d.calculated_reward = (commissionable_amount * (d.reward_amount || 0) / 100);
            } else if (d.reward_mode === 'Fixed') {
                d.calculated_reward = (d.reward_amount || 0);
            } else if (d.reward_mode === 'Material Consumption') {
                if (d.target_item && d.unit_quantity) {
                    var target_qty = 0;
                    $.each(frm.doc.table_66 || [], function (j, p) {
                        if (p.item_code === d.target_item) {
                            target_qty += p.qty;
                        }
                    });
                    d.calculated_reward = (target_qty / d.unit_quantity) * (d.reward_per_unit || 0);
                } else {
                    d.calculated_reward = 0;
                }
            }
        });
        frm.refresh_field('maintenance_assignments');
    }
});

frappe.ui.form.on('Maintenance Assignment', {
    reward_mode: function (frm, cdt, cdn) {
        var d = locals[cdt][cdn];
        toggle_assignment_fields(frm, d);
        frm.trigger('calculate_rewards');
    },
    reward_amount: function (frm, cdt, cdn) {
        frm.trigger('calculate_rewards');
    },
    reward_per_unit: function (frm, cdt, cdn) {
        frm.trigger('calculate_rewards');
    },
    unit_quantity: function (frm, cdt, cdn) {
        frm.trigger('calculate_rewards');
    },
    target_item: function (frm, cdt, cdn) {
        frm.trigger('calculate_rewards');
    },
    maintenance_assignments_add: function (frm, cdt, cdn) {
        var d = locals[cdt][cdn];
        toggle_assignment_fields(frm, d);
    }
});

function toggle_assignment_fields(frm, d) {
    var grid_row = frm.fields_dict.maintenance_assignments.grid.get_row(d.name);
    if (!grid_row) return;

    if (d.reward_mode === 'Material Consumption') {
        grid_row.toggle_display('reward_amount', false);
        grid_row.toggle_display('target_item', true);
        grid_row.toggle_display('unit_quantity', true);
        grid_row.toggle_display('reward_per_unit', true);
    } else {
        grid_row.toggle_display('reward_amount', true);
        grid_row.toggle_display('target_item', false);
        grid_row.toggle_display('unit_quantity', false);
        grid_row.toggle_display('reward_per_unit', false);
    }
}
