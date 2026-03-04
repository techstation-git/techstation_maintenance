// Copyright (c) 2020, Tech Station and contributors
// For license information, please see license.txt

frappe.ui.form.on('Maintenance Invoice', {
    show_data: function (frm) {
        let d = new frappe.ui.Dialog({
            title: 'Select Payment Method',
            fields: [
                {
                    label: 'POS Profile',
                    fieldname: 'pos_profile',
                    fieldtype: 'Link',
                    options: 'POS Profile',
                    default: frm.doc.pos_profile,
                    reqd: 1,
                    get_query() {

                        return {
                            filters: [
                                ["POS Profile User", 'user', '=', frappe.session.user],
                                ["POS Profile", 'disabled', '=', 0],
                            ]
                        }
                    },
                },
                {
                    label: 'Payment Method',
                    fieldname: 'payment_method',
                    fieldtype: 'Link',
                    options: 'Mode of Payment',
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
                    label: 'Net Total',
                    fieldname: 'total',
                    fieldtype: 'Currency',
                    default: frm.doc.service_net_total,
                    read_only: 1
                },
                {
                    label: 'Outstanding Amount',
                    fieldname: 'outstanding_amount',
                    fieldtype: 'Currency',
                    default: frm.doc.outstanding_amount,
                    read_only: 1
                },
                {
                    fieldname: 'cb_3',
                    fieldtype: 'Column Break'
                },
                {
                    label: 'Paid Amount',
                    fieldname: 'paid',
                    fieldtype: 'Currency',
                    default: frm.doc.paid_amount,
                    read_only: 1
                },
                {
                    label: 'Allocated Amount',
                    fieldname: 'net_total',
                    fieldtype: 'Currency',
                    default: frm.doc.outstanding_amount,
                    reqd: 1
                }
            ],
            primary_action_label: 'Submit',
            primary_action(values) {
                frm.set_value("payment_method", values.payment_method);
                if (values.net_total > 0.0) {
                    if (values.net_total > values.outstanding_amount) {
                        frappe.throw("Allocated Amount must be less or equal to Outstanding Amount")
                    }
                    frappe.call({
                        "method": "maintenance_system.maintenance_system.doctype.maintenance_invoice.maintenance_invoice.make_payment_entry_invoice",
                        args: {
                            doc: frm.doc.name,
                            mode: frm.doc.payment_method,
                            allocated_amount: values.net_total,
                            outstanding: values.outstanding_amount - values.net_total,
                        },
                        callback: function (r) {
                            frm.reload_doc()
                        }
                    });
                }
                else {
                    frappe.throw("Please Enter valid Outstanding Amount")
                }
                d.hide();
            }
        });

        d.show();

    }
});


frappe.ui.form.on('Maintenance Invoice', {
    refresh: function (frm) {
        if (!!frappe.user_roles.includes("Maintenance Manager")) {

        }
        if (frm.doc.docstatus == 1 && frm.doc.status != "Paid" && frm.doc.outstanding_amount > 0.0) {
            frm.add_custom_button(__('Maintenance Payment'),

                function () {
                    frm.trigger("show_data");

                });
        }

        // if(frm.doc.docstatus == 1){
        frm.add_custom_button(__("POS Receipt"), function () {
            window.open("/printview?doctype=Maintenance%20Invoice&name=" + frm.doc.name + "&trigger_print=1&format=POS Receipt Maintenance Invoice&no_letterhead=1&letterhead=No Letterhead&settings={}&_lang=en-US")
        }).css({ 'backgroudcolor': 'black', 'font-weight': 'bold' });
        // }

        if (frm.doc.docstatus == 1) {
            frm.add_custom_button(__('Veiw Account Ledger'),

                function () {
                    frappe.set_route("query-report", "General Ledger");

                });
        }


    }
});




frappe.ui.form.on('Maintenance Invoice', {
    refresh: function (frm) {
        if (!frappe.user_roles.includes("Maintenance Manager")) {
            cur_frm.set_df_property("service", "read_only", 1)
            // cur_frm.set_df_property("items", "read_only", 1)
        } else {
            cur_frm.set_df_property("service", "read_only", 0)
            cur_frm.set_df_property("items", "read_only", 0)
        }
    },
    validate: function (frm) {
        frm.trigger("company_address")
    },
    company_address(frm) {
        if (frm.doc.company_address) {
            frappe.call({
                method: "frappe.contacts.doctype.address.address.get_address_display",
                args: { "address_dict": frm.doc.company_address },
                callback: function (r) {
                    if (r.message) {
                        frm.set_value("company_address_display", r.message)
                    }
                }
            })
        } else {
            frm.set_value("company_address_display", "");
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

    }
});






frappe.ui.form.on("Maintenance Invoice", "onload", function (frm) {
    cur_frm.set_query("maintenance_products_receipt", function () {
        return {
            "filters": {
                "customer": frm.doc.customer,
                "maintenance_processing": frm.doc.maintenance_processing,
                "docstatus": 1,
                "status": "Delivered"
            }
        };
    });
});


frappe.ui.form.on("Maintenance Invoice", "warranty_template_repair", function (frm) {
    if (frm.doc.warranty_template_repair) {
        frappe.model.with_doc("Warranty Template", frm.doc.warranty_template_repair, function () {
            var warranty = frappe.model.get_doc("Warranty Template", frm.doc.warranty_template_repair);
            if (!frm.doc.warranty_start_date_repair) {
                frm.set_value("warranty_start_date_repair", frm.doc.posting_date)
                frm.set_value("warranty_expiry_date_repair", frappe.datetime.add_days(frm.doc.posting_date, warranty.warranty_period))
            }

        });
    } else {
        frm.set_value("warranty_start_date_repair", "")
        frm.set_value("warranty_expiry_date_repair", "")
    }
});

frappe.ui.form.on('Maintenance Invoice', {
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




//Maintenance Invoice Settings

frappe.ui.form.on("Maintenance Invoice Item", {
    item_code: function (frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        if (frm.doc.delivery_date) {
            row.delivery_date = frm.doc.delivery_date;
            refresh_field("delivery_date", cdn, "items");
        } else {
            frm.script_manager.copy_from_first_row("items", row, ["delivery_date"]);
        }
    },
    delivery_date: function (frm, cdt, cdn) {
        if (!frm.doc.delivery_date) {
            erpnext.utils.copy_value_in_all_rows(frm.doc, cdt, cdn, "items", "delivery_date");
        }
    }
});

//Calculate Quantity and Amount For Service Items

frappe.ui.form.on("Maintenance Invoice Item", {
    item_code: function (frm, cdt, cdn) {


        var total = 0;
        var qty = 0;
        frm.doc.items.forEach(function (d) {
            frappe.db.get_value("Item Price", {
                "item_code": d.item_code, "price_list": frm.doc.price_list
            }, ['price_list_rate'], function (value) {
                if (typeof value.price_list_rate !== "undefined") {
                    total += value.price_list_rate * d.qty;
                    frm.set_value("total_amount", total);
                    var service_t = typeof frm.doc.service_total !== "undefined" ? frm.doc.service_total : 0;
                    frm.set_value("service_net_total", service_t + total)
                    var tax_t = typeof frm.doc.total_taxes_and_charges !== "undefined" ? frm.doc.total_taxes_and_charges : 0;
                    frm.set_value("grand_total", service_t + total + tax_t)
                }
            });
            qty += d.qty;
        });
        frm.set_value("total_qty", qty);
        frm.set_value("spare_part_quantity", qty);
        refresh_field("spare_part_quantity");
        refresh_field("service_net_total");
        refresh_field("grand_total");
        refresh_field("total_qty");
        refresh_field("total_amount");

    },
    qty: function (frm, cdt, cdn) {


        var total = 0;
        var qty = 0;
        frm.doc.items.forEach(function (d) {
            frappe.db.get_value("Item Price", {
                "item_code": d.item_code, "price_list": frm.doc.price_list
            }, ['price_list_rate'], function (value) {
                if (typeof value.price_list_rate !== "undefined") {
                    total += value.price_list_rate * d.qty;
                    frm.set_value("total_amount", total);
                    var service_t = typeof frm.doc.service_total !== "undefined" ? frm.doc.service_total : 0;
                    frm.set_value("service_net_total", service_t + total)
                    var tax_t = typeof frm.doc.total_taxes_and_charges !== "undefined" ? frm.doc.total_taxes_and_charges : 0;
                    frm.set_value("grand_total", service_t + total + tax_t)
                }
            });
            qty += d.qty;
        });
        frm.set_value("total_qty", qty);
        frm.set_value("spare_part_quantity", qty);
        refresh_field("spare_part_quantity");
        refresh_field("service_net_total");
        refresh_field("grand_total");
        refresh_field("total_qty");
        refresh_field("total_amount");

    },
    items_remove: function (frm, cdt, cdn) {
        var total = 0;
        var qty = 0;
        frm.doc.items.forEach(function (d) { total += d.amount; qty += d.qty; });
        frm.set_value("total_amount", total);
        frm.set_value("total_qty", qty);
        frm.set_value("spare_part_quantity", qty);
        frm.set_value("service_net_total", frm.doc.service_total + total)
        var tax_t = typeof frm.doc.total_taxes_and_charges !== "undefined" ? frm.doc.total_taxes_and_charges : 0;
        frm.set_value("grand_total", frm.doc.service_total + total + tax_t)
        refresh_field("spare_part_quantity");
        refresh_field("service_net_total");
        refresh_field("grand_total");
        refresh_field("total_qty");
        refresh_field("total_amount");

    }
});


//Calculate Quantity and Amount For Service Items

frappe.ui.form.on("Maintenance Invoice Service", {
    maintenance_service: function (frm, cdt, cdn) {
        var total = 0;
        frm.doc.service.forEach(function (d) { total += d.price; });
        frm.set_value("service_total", total);
        var total_t = typeof frm.doc.total_amount !== "undefined" ? frm.doc.total_amount : 0;
        var tax_t = typeof frm.doc.total_taxes_and_charges !== "undefined" ? frm.doc.total_taxes_and_charges : 0;
        frm.set_value("service_net_total", total_t + total)
        frm.set_value("grand_total", total_t + total + tax_t)
        refresh_field("grand_total");
        refresh_field("service_net_total");
        refresh_field("service_total");

    },
    service_remove: function (frm, cdt, cdn) {
        var total = 0;
        frm.doc.services.forEach(function (d) { total += d.price; });
        frm.set_value("service_total", total);
        var total_t = typeof frm.doc.total_amount !== "undefined" ? frm.doc.total_amount : 0;
        var tax_t = typeof frm.doc.total_taxes_and_charges !== "undefined" ? frm.doc.total_taxes_and_charges : 0;
        frm.set_value("service_net_total", total_t + total)
        frm.set_value("grand_total", total_t + total + tax_t)
        refresh_field("grand_total");
        refresh_field("service_net_total");
        refresh_field("service_total");

    }
});

frappe.ui.form.on('Maintenance Invoice', {
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
        if (!frm.doc.price_list && frm.doc.docstatus == 0) {
            frappe.model.with_doc("Maintenance System Settings", frm.doc.trigger, function () {
                var tabletransfer = frappe.model.get_doc("Maintenance System Settings");
                frm.set_value("price_list", tabletransfer.default_price_list)
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
                cur_frm.refresh_field("price_list");
            });
        }

    },
    delivery_date: function (frm) {
        if (frm.doc.delivery_date < frm.doc.posting_date) {
            frm.set_value("delivery_date", "")
            frappe.throw("Delivery Date Should not Less than Current Date")
        }
        $.each(frm.doc.items || [], function (i, d) {
            d.delivery_date = frm.doc.delivery_date;
        });
        refresh_field("items");
    },
    before_save: function (frm) {
        if (frm.doc.grand_total && !frm.doc.payment_received) {
            frm.set_value("outstanding_amount", frm.doc.service_net_total)
        }
        $.each(frm.doc.items || [], function (i, d) {
            if (d.delivery_date < frm.doc.posting_date) {
                frappe.model.set_value(d.doctype, d.name, "delivery_date", "");
                frappe.throw("Delivery Date Should not Less than Current Date")
            }
            frm.doc.delivery_date = d.delivery_date
        });
    },
    total_taxes_and_charges: function (frm) {
        var total_t = typeof frm.doc.service_net_total !== "undefined" ? frm.doc.service_net_total : 0;
        var tax_t = typeof frm.doc.total_taxes_and_charges !== "undefined" ? frm.doc.total_taxes_and_charges : 0;
        frm.set_value("grand_total", total_t + tax_t)
    }


});



frappe.ui.form.on('Maintenance Invoice Service', {
    refresh(frm, cdt, cdn) {
        var df = frappe.meta.get_docfield("Maintenance Order Items", "price", cur_frm.doc.name);
        df.hidden = 1;
    }
})


frappe.ui.form.on('Maintenance Invoice Item', {
    item_code(frm, cdt, cdn) {
        if (frm.doc.price_list) {
            var data = locals[cdt][cdn]
            frappe.db.get_value("Item Price", {
                "item_code": data.item_code, "price_list": frm.doc.price_list
            }, ['price_list_rate'], function (value) {
                if (typeof value.price_list_rate !== "undefined") {
                    data.rate = value.price_list_rate
                    data.amount = data.qty * value.price_list_rate
                    refresh_field("items");
                } else {
                    frappe.throw("Prease Create a Item Price For " + frm.doc.price_list + "Price List")
                }
            });
            refresh_field("items")
        } else {
            frappe.throw("Prease Select a Default Price List in Maintenance System Settings" + frm.doc.price_list)
        }

    },
    qty(frm, cdt, cdn) {
        var data = locals[cdt][cdn]
        data.amount = data.qty * data.rate
        refresh_field("items");
    }
})

//Calculate Taxes and Charges

frappe.ui.form.on("Maintenance Invoice", "service_net_total", function (frm) {
    if (frm.doc.sales_taxes_and_charges_template) {
        var taxes = 0;
        var value = frm.doc.service_net_total;
        frappe.model.with_doc("Sales Taxes and Charges Template", frm.doc.sales_taxes_and_charges_template, function () {
            cur_frm.clear_table("tax");
            var tabletransfer = frappe.model.get_doc("Sales Taxes and Charges Template", frm.doc.sales_taxes_and_charges_template);
            $.each(tabletransfer.taxes, function (index, row) {
                var d = frm.add_child("tax");
                d.account_head = row.account_head;
                d.cost_center = row.cost_center;
                d.rate = row.rate;
                d.tax_amount = (row.rate / 100) * frm.doc.service_net_total;
                value = d.tax_amount + value;
                d.total = value;
                taxes = taxes + d.tax_amount;
                frm.set_value("total_taxes_and_charges", taxes);
                var service_t = typeof frm.doc.service_total !== "undefined" ? frm.doc.service_total : 0;
                if (typeof frm.doc.total_amount !== "undefined") {
                    frm.set_value("grand_total", frm.doc.total_amount + service_t + frm.doc.total_taxes_and_charges)
                } else {
                    frm.set_value("grand_total", service_t + frm.doc.total_taxes_and_charges)
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
        if (typeof frm.doc.total_amount !== "undefined") {
            frm.set_value("grand_total", frm.doc.total_amount + service_t + frm.doc.total_taxes_and_charges)
        } else {
            frm.set_value("grand_total", service_t + frm.doc.total_taxes_and_charges)
        }
        refresh_field("grand_total");
    }
});

frappe.ui.form.on("Maintenance Invoice", "sales_taxes_and_charges_template", function (frm) {
    if (frm.doc.sales_taxes_and_charges_template) {
        var taxes = 0;
        var value = frm.doc.service_net_total;
        frappe.model.with_doc("Sales Taxes and Charges Template", frm.doc.sales_taxes_and_charges_template, function () {
            cur_frm.clear_table("tax");
            var tabletransfer = frappe.model.get_doc("Sales Taxes and Charges Template", frm.doc.sales_taxes_and_charges_template);
            $.each(tabletransfer.taxes, function (index, row) {
                var d = frm.add_child("tax");
                d.account_head = row.account_head;
                d.cost_center = row.cost_center;
                d.rate = row.rate;
                d.tax_amount = (row.rate / 100) * frm.doc.service_net_total;
                value = d.tax_amount + value;
                d.total = value;
                taxes = taxes + d.tax_amount;
                frm.set_value("total_taxes_and_charges", taxes);
                if (typeof frm.doc.total_amount !== "undefined") {
                    frm.set_value("grand_total", frm.doc.total_amount + frm.doc.service_total + taxes)
                } else {
                    frm.set_value("grand_total", frm.doc.service_total + taxes)
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
        if (typeof frm.doc.total_amount !== "undefined") {
            frm.set_value("grand_total", frm.doc.total_amount + service_t + frm.doc.total_taxes_and_charges)
        } else {
            frm.set_value("grand_total", service_t + frm.doc.total_taxes_and_charges)
        }
        refresh_field("grand_total");
    }
});


frappe.ui.form.on("Maintenance Invoice", {
    refresh: function (frm) {
        if (!frm.doc.table_127) {
            $(".grid-add-row").hide();
            $(".grid-remove-rows").hide();
        }

    }
});





// Caclulating Discount
frappe.ui.form.on("Maintenance Invoice", {
    refresh: function (frm) {
        if (!!!frappe.user_roles.includes("Maintenance Supervisor")) {
            cur_frm.set_df_property("additional_dicount", "read_only", 1)
            cur_frm.set_df_property("discount", "read_only", 1)
            cur_frm.set_df_property("warranty_bearing_percentage", "read_only", 1)
            cur_frm.set_df_property("table_127", "read_only", 1)
        } else {
            cur_frm.set_df_property("additional_dicount", "read_only", 0)
            cur_frm.set_df_property("discount", "read_only", 0)
            cur_frm.set_df_property("additional_discount_percentage", "read_only", 0)
            // cur_frm.set_df_property("warranty_bearing_percentage", "read_only", 0)
            cur_frm.set_df_property("table_127", "read_only", 0)
        }
    },
    additional_discount_percentage: function (frm, cdt, cdn) {
        var total = 0;
        var discount_amount = 0.0;
        if (frm.doc.additional_dicount == "Net Total") {
            discount_amount = frm.doc.service_net_total * (frm.doc.additional_discount_percentage / 100)

        }
        else if (frm.doc.additional_dicount == "Grand Total") {
            discount_amount = frm.doc.grand_total * (frm.doc.additional_discount_percentage / 100)
        }

        frm.set_value("discount", discount_amount)


    },
    discount: function (frm, cdt, cdn) {

        var total = 0.0;
        var discount_amount = 0.0;
        if (frm.doc.additional_dicount == "Net Total") {
            discount_amount = (frm.doc.discount / frm.doc.service_net_total) * 100
        }
        else if (frm.doc.additional_dicount == "Grand Total") {
            discount_amount = (frm.doc.discount / frm.doc.grand_total) * 100
        }


        frm.set_value("additional_discount_percentage", discount_amount)


    },
    before_save(frm) {
        var total = 0.0;
        var discount_amount = frm.doc.discount;

        if (discount_amount > 0) {
            total = frm.doc.service_net_total + frm.doc.total_taxes_and_charges - discount_amount
            frm.set_value("grand_total", frm.doc.service_net_total + frm.doc.total_taxes_and_charges - discount_amount)
            frm.set_value("outstanding_amount", total)
        } else {
            frm.set_value("grand_total", frm.doc.service_net_total + frm.doc.total_taxes_and_charges)
            frm.set_value("outstanding_amount", frm.doc.service_net_total + frm.doc.total_taxes_and_charges)
        }
        refresh_field("grand_total");
        refresh_field("discount");
        refresh_field("outstanding_amount");
    }

});



//Warranty Template Repair Filter

frappe.ui.form.on("Maintenance Invoice", "onload", function (frm) {
    frm.set_query("warranty_template_repair", function () {
        return {
            "filters": {
                "enabled": 1,
                "dedicated_repair_warranty": 1
            }
        };
    });
});


// #Calculate Total Warranty
/*frappe.ui.form.on("Maintenance Invoice", "warranty_apply", function (frm) {

    if (frm.doc.warranty_apply == 1) {
        cur_frm.set_df_property("additional_dicount", "read_only", 1)
        cur_frm.set_df_property("discount", "read_only", 1)
        cur_frm.set_df_property("additional_discount_percentage", "read_only", 1)
        if (frm.doc.warranty_bearing_rate.length >= 1) {
            var warranty_bearing_percentage = 0;
            frm.doc.warranty_bearing_rate.forEach(function (d) {
                warranty_bearing_percentage += d.repair_tolerence

            });
            var percentage = warranty_bearing_percentage;
            frm.set_value("warranty_bearing_percentage", percentage)
            var net_total = 0;
            if (frm.doc.service_total) {
                net_total += frm.doc.service_total
            }
            if (frm.doc.total_amount) {
                net_total += frm.doc.total_amount
            }
            var total_net = net_total - (net_total * percentage / 100)
            cur_frm.refresh_field("warranty_bearing_percentage");
            frm.set_value("warranty_total", net_total * percentage / 100)
            frm.set_value("service_net_total", total_net)
            cur_frm.refresh_field("warranty_total");
            cur_frm.refresh_field("service_net_total");
        }

        // warranty_bearing_percentage
    } else {
        cur_frm.set_df_property("additional_dicount", "read_only", 0)
        cur_frm.set_df_property("discount", "read_only", 0)
        cur_frm.set_df_property("additional_discount_percentage", "read_only", 0)
        var net_total = 0;
        if (frm.doc.service_total) {
            net_total += frm.doc.service_total
        }
        if (frm.doc.total_amount) {
            net_total += frm.doc.total_amount
        }
        var total_net = net_total
        frm.set_value("warranty_total", 0)
        frm.set_value("warranty_bearing_percentage", 0)
        frm.set_value("service_net_total", total_net)
        cur_frm.refresh_field("warranty_total");
        cur_frm.refresh_field("service_net_total");
        cur_frm.refresh_field("warranty_bearing_percentage");
    }

});*/


// #Calculate Total Warranty
frappe.ui.form.on("Maintenance Invoice", "refresh", function (frm) {

    if (frm.doc.warranty_apply == 1) {
        cur_frm.set_df_property("additional_dicount", "read_only", 1)
        cur_frm.set_df_property("discount", "read_only", 1)
        cur_frm.set_df_property("additional_discount_percentage", "read_only", 1)

        // warranty_bearing_percentage
    } else {
        cur_frm.set_df_property("additional_dicount", "read_only", 0)
        cur_frm.set_df_property("discount", "read_only", 0)
        cur_frm.set_df_property("additional_discount_percentage", "read_only", 0)
    }

});


frappe.ui.form.on("Maintenance Invoice", "edit_posting_date_and_time", function (frm) {
    if (frm.doc.edit_posting_date_and_time == 1) {
        frm.set_df_property("posting_date", "read_only", 0)
        frm.set_df_property("posting_time", "read_only", 0)
    } else {
        frm.set_df_property("posting_date", "read_only", 1)
        frm.set_df_property("posting_time", "read_only", 1)
    }
});
frappe.ui.form.on("Maintenance Invoice", "edit_delivery_date", function (frm) {
    if (frm.doc.edit_delivery_date == 1) {
        frm.set_df_property("delivery_date", "read_only", 0)
    } else {
        frm.set_df_property("delivery_date", "read_only", 1)
    }
});

frappe.ui.form.on("Maintenance Invoice", {
    /*warranty_bearing_percentage: function (frm) {
        frm.trigger('abc')
    },*/
    validate: function (frm) {
        frm.doc.warranty_bearing_rate = [];
        erpnext.utils.map_current_doc({
            method: "maintenance_system.maintenance_system.doctype.maintenance_invoice.maintenance_invoice.fetch_template",
            source_name: frm.doc.maintenance_item,
            frm: frm
        });

    },
    abc: function (frm) {
        if (frm.doc.warranty_bearing_percentage > 100) {
            frappe.throw("Warranty Bearing Percentage Should not Greater than 100")
        } else {
            var net_total = 0;
            var percentage = frm.doc.warranty_bearing_percentage;
            if (frm.doc.service_total) {
                net_total += frm.doc.service_total
            }
            if (frm.doc.total_amount) {
                net_total += frm.doc.total_amount
            }
            var total_net = net_total - (net_total * percentage / 100)
            frm.set_value("warranty_total", net_total * percentage / 100)
            frm.set_value("service_net_total", total_net)
            cur_frm.refresh_field("warranty_total");
            cur_frm.refresh_field("service_net_total");

        }
    }

});
