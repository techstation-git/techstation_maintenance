// Copyright (c) 2026, Tech Station and contributors
// For license information, please see license.txt

frappe.ui.form.on('Technician Custody', {
    refresh: function (frm) {
        // Add "Return Custody" button if custody is issued
        if (frm.doc.docstatus === 1 && frm.doc.custody_status !== "Fully Returned") {
            frm.add_custom_button(__('Return Custody'), function () {
                show_return_custody_dialog(frm);
            }).addClass('btn-primary');
        }

        // Show status indicator
        if (frm.doc.custody_status) {
            let color = 'blue';
            if (frm.doc.custody_status === 'Overdue') {
                color = 'red';
            } else if (frm.doc.custody_status === 'Fully Returned') {
                color = 'green';
            } else if (frm.doc.custody_status === 'Issued') {
                color = 'orange';
            }

            frm.dashboard.add_indicator(
                __('{0}', [frm.doc.custody_status]),
                color
            );
        }
    }
});

function show_return_custody_dialog(frm) {
    // Prepare items data with return quantities
    let items_data = frm.doc.items.map(item => {
        return {
            ...item,
            qty_to_return: Math.max(0, (item.qty_issued || 0) - (item.qty_returned || 0))
        };
    });

    let d = new frappe.ui.Dialog({
        title: __('Return Custody Items'),
        fields: [
            {
                fieldtype: 'HTML',
                options: `<p class="text-muted">Mark items as returned. You can return all or part of the custody.</p>`
            },
            {
                fieldtype: 'Section Break'
            },
            {
                label: __('Items'),
                fieldname: 'items',
                fieldtype: 'Table',
                cannot_add_rows: true,
                cannot_delete_rows: true,
                in_place_edit: true,
                data: items_data,
                get_data: () => {
                    return items_data;
                },
                fields: [
                    {
                        label: __('Item'),
                        fieldname: 'item_code',
                        fieldtype: 'Link',
                        options: 'Item',
                        in_list_view: 1,
                        read_only: 1
                    },
                    {
                        label: __('Issued'),
                        fieldname: 'qty_issued',
                        fieldtype: 'Float',
                        in_list_view: 1,
                        read_only: 1
                    },
                    {
                        label: __('Already Returned'),
                        fieldname: 'qty_returned',
                        fieldtype: 'Float',
                        in_list_view: 1,
                        read_only: 1
                    },
                    {
                        label: __('Return Now'),
                        fieldname: 'qty_to_return',
                        fieldtype: 'Float',
                        in_list_view: 1,
                        reqd: 0
                    },
                    {
                        label: __('Condition'),
                        fieldname: 'return_condition',
                        fieldtype: 'Select',
                        options: '\nWorking\nDamaged\nConsumed\nSurplus',
                        in_list_view: 1
                    }
                ]
            }
        ],
        primary_action_label: __('Confirm Return'),
        primary_action(values) {
            // Calculate total return quantities
            let has_returns = false;
            let updates = [];

            values.items.forEach((item, idx) => {
                let qty_to_return = parseFloat(item.qty_to_return || 0);

                if (qty_to_return > 0) {
                    has_returns = true;
                    let new_qty_returned = (frm.doc.items[idx].qty_returned || 0) + qty_to_return;

                    updates.push({
                        name: frm.doc.items[idx].name,
                        qty_returned: new_qty_returned,
                        return_condition: item.return_condition
                    });
                }
            });

            if (!has_returns) {
                frappe.msgprint(__('Please specify quantities to return'));
                return;
            }

            // Update the custody record
            frappe.call({
                method: 'frappe.client.set_value',
                args: {
                    doctype: 'Custody Item',
                    name: updates.map(u => u.name),
                    fieldname: updates.reduce((obj, u) => {
                        obj[u.name] = {
                            qty_returned: u.qty_returned,
                            return_condition: u.return_condition
                        };
                        return obj;
                    }, {})
                },
                callback: function (r) {
                    if (!r.exc) {
                        frappe.msgprint(__('Custody items returned successfully!'));
                        frm.reload_doc();
                        d.hide();

                        // Update Maintenance Order
                        update_maintenance_order_custody_status(frm);
                    }
                }
            });
        }
    });

    d.show();
}

function update_maintenance_order_custody_status(frm) {
    if (frm.doc.maintenance_order) {
        frappe.call({
            method: 'frappe.client.get_value',
            args: {
                doctype: 'Technician Custody',
                filters: { name: frm.doc.name },
                fieldname: ['custody_status']
            },
            callback: function (r) {
                if (r.message && r.message.custody_status === 'Fully Returned') {
                    frappe.call({
                        method: 'frappe.client.set_value',
                        args: {
                            doctype: 'Maintenance Order',
                            name: frm.doc.maintenance_order,
                            fieldname: {
                                custody_returned: 1,
                                custody_status: 'Fully Returned'
                            }
                        }
                    });
                }
            }
        });
    }
}
