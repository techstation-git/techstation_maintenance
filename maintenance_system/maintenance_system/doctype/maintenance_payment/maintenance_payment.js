// Copyright (c) 2020, Tech Station and contributors
// For license information, please see license.txt

frappe.ui.form.on('Maintenance Payment', {
        paid_amount: function (frm) {
                //frm.set_value("unallocated_amount", frm.doc.paid_amount);
                frm.trigger("reset_received_amount");
        },
        reset_received_amount: function(frm) {
		if(!frm.set_paid_amount_based_on_received_amount &&
				(frm.doc.paid_from_account_currency == frm.doc.paid_to_account_currency)) {

			//frm.set_value("received_amount", frm.doc.paid_amount);

			if(frm.doc.source_exchange_rate) {
				frm.set_value("target_exchange_rate", frm.doc.source_exchange_rate);
			}
			//frm.set_value("base_received_amount", frm.doc.base_paid_amount);
		}

		if(frm.doc.payment_type == "Receive")
			frm.events.allocate_party_amount_against_ref_docs(frm, frm.doc.paid_amount, 1);
		else
			frm.events.set_unallocated_amount(frm);
	},
});


frappe.ui.form.on("Maintenance Payment", "onload", function (frm) {
        cur_frm.set_query("paid_to", function () {
                return {
                        "filters": {
                                "is_group": 0,
                                "company": frm.doc.company,
                                "account_type": ["in", "Cash, Bank"]
                        }
                };
        });
});

frappe.ui.form.on("Maintenance Payment", "onload", function (frm) {
        cur_frm.set_query("cost_center", function () {
                return {
                        "filters": {
                                "is_group": 0,
                                "company": frm.doc.company
                        }
                };
        });
});

frappe.ui.form.on("Maintenance Payment", "onload", function (frm) {
        cur_frm.set_query("paid_from", function () {
                return {
                        "filters": {
                                "is_group": 0,
                                "company": frm.doc.company,
                                "account_type": "Receivable"
                        }
                };
        });
});

frappe.ui.form.on('Maintenance Payment', 'paid_to', function (frm) {
        return frappe.call({
                method: "erpnext.accounts.doctype.payment_entry.payment_entry.get_account_details",
                args: {
                        "account": frm.doc.paid_to,
                        "date": frm.doc.posting_date,
                        "cost_center": frm.doc.cost_center
                },

                callback: function (r) {
                        frm.set_value("paid_to_account_balance", r.message.account_balance);

                }
        })
});

frappe.ui.form.on('Maintenance Payment', 'paid_from', function (frm) {
        return frappe.call({
                method: "erpnext.accounts.doctype.payment_entry.payment_entry.get_account_details",
                args: {
                        "account": frm.doc.paid_from,
                        "date": frm.doc.posting_date,
                        "cost_center": frm.doc.cost_center
                },

                callback: function (r) {
                        frm.set_value("paid_from_account_balance", r.message.account_balance);

                }
        })
});


frappe.ui.form.on('Maintenance Payment', 'party', function (frm) {
        return frappe.call({
                method: "erpnext.accounts.doctype.payment_entry.payment_entry.get_party_details",
                args: {
                        date: frm.doc.posting_date,
                        party_type: "Customer",
                        party: frm.doc.party,
                        company: frm.doc.company,
                        cost_center: frm.doc.cost_center
                },

                callback: function (r) {
                        frm.set_value("party_balance", r.message.party_balance);
                }
        })
});



frappe.ui.form.on("Maintenance Payment", {
        get_outstanding_invoice: function (frm) {
                if (frm.doc.get_outstanding_invoice == 1) {
                        cur_frm.refresh();
                        cur_frm.clear_table("references");
                        cur_frm.refresh_fields();

                        frappe.call({
                                "method": "maintenance_system.maintenance_system.doctype.maintenance_payment.maintenance_payment.getMINV",
                                args: {
                                        party: frm.doc.party
                                },
                                callback: function (r) {
                                        var len = r.message.length;
                                        for (var i = 0; i < len; i++) {
                                                var row = frm.add_child("references");
                                                row.reference_doctype = "Maintenance Invoice";
                                                row.reference_name = r.message[i][0];
                                                row.due_date = r.message[i][1];
                                                row.total_amount = r.message[i][2];
                                                row.outstanding_amount = r.message[i][3];
                                        }
                                        cur_frm.refresh();
                                }
                        });
                }
                if (frm.doc.get_outstanding_invoice == 0) {
                        cur_frm.refresh();
                        cur_frm.clear_table("references");
                }
        }

});

frappe.ui.form.on("Maintenance Payment Reference", "allocated_amount", function (frm, cdt, cdn) {
        cur_frm.refresh_fields();
        var d = locals[cdt][cdn];
        var ref = frm.doc.references;
        var total = 0;
        frappe.model.set_value(d.doctype, d.name, "pending", d.outstanding_amount - d.allocated_amount);
        for (var j in ref) {

                if (ref[j].allocated_amount <= ref[j].outstanding_amount) {
                        total = total + ref[j].allocated_amount;
                        frm.set_value("total_allocated_amount", total);
                        frm.set_value("unallocated_amount", frm.doc.paid_amount - total);
                }
                if (ref[j].allocated_amount > ref[j].outstanding_amount) {
                        frappe.model.set_value(d.doctype, d.name, "allocated_amount", d.outstanding_amount);
                }
        }
});

frappe.ui.form.on('Maintenance Payment', 'validate', function (frm) {
        if (frm.doc.unallocated_amount === 0 && frm.doc.get_outstanding_invoice === 0) {
                frm.set_value("unallocated_amount", frm.doc.paid_amount);
        }

        if (frm.doc.unallocated_amount < 0) {
                frappe.throw("Unallocated Amount Can Not Be In Negative, Either Change Paid Amount or Allocation Amount in Invoice");
                validated = false;
        }
});

frappe.ui.form.on('Maintenance Payment', 'paid_amount', function (frm) {
        if (frm.doc.get_outstanding_invoice === 0) {
                frm.set_value("unallocated_amount", (frm.doc.paid_amount - frm.doc.total_allocated_amount));
        }
});
