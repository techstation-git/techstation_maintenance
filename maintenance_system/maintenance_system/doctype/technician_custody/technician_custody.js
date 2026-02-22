frappe.ui.form.on('Technician Custody', {
    refresh: function (frm) {
        if (frm.doc.docstatus == 1 && frm.doc.status != "Fully Returned") {
            frm.add_custom_button(__("Return Items"), function () {
                frm.trigger("make_return_stock_entry");
            });
        }
    },
    make_return_stock_entry: function (frm) {
        let d = new frappe.ui.Dialog({
            title: __("Return Custody Items"),
            fields: [
                {
                    label: __("Items"),
                    fieldname: "items",
                    fieldtype: "Table",
                    fields: [
                        {
                            label: __("Item"),
                            fieldname: "item_code",
                            fieldtype: "ReadOnly",
                            in_list_view: 1
                        },
                        {
                            label: __("Qty Issued"),
                            fieldname: "qty_issued",
                            fieldtype: "ReadOnly",
                            in_list_view: 1
                        },
                        {
                            label: __("Return Qty"),
                            fieldname: "qty_returned_now",
                            fieldtype: "Float",
                            in_list_view: 1,
                            reqd: 1
                        },
                        {
                            label: __("Type"),
                            fieldname: "item_type",
                            fieldtype: "ReadOnly",
                            in_list_view: 1
                        },
                        {
                            label: __("Condition/Usage"),
                            fieldname: "return_condition",
                            fieldtype: "Select",
                            options: "\nWorking\nDamaged\nConsumed\nSurplus",
                            in_list_view: 1,
                            reqd: 1
                        }
                    ],
                    data: frm.doc.items.map(item => ({
                        item_code: item.item_code,
                        qty_issued: item.qty_issued,
                        qty_returned_now: item.qty_issued - (item.qty_returned || 0),
                        item_type: item.item_type,
                        return_condition: item.item_type == "Tool" ? "Working" : "Consumed"
                    }))
                }
            ],
            primary_action_label: __("Create Return Entry"),
            primary_action(values) {
                frappe.call({
                    method: "create_return_stock_entry",
                    doc: frm.doc,
                    args: {
                        return_items: values.items
                    },
                    callback: function (r) {
                        frm.reload_doc();
                        d.hide();
                    }
                });
            }
        });
        d.show();
    }
});
