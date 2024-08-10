// Copyright (c) 2022, Tech Station and contributors
// For license information, please see license.txt

frappe.ui.form.on('Commission Payment', {
    refresh: function (frm) {
        if(frm.doc.docstatus <1){
            frm.set_value("from_date", frappe.datetime.add_months(frappe.datetime.get_today(), -1))
            frm.set_value("to_date", frappe.datetime.get_today())
        }
        
        frappe.model.with_doc("Maintenance System Settings", frm.doc.trigger, function () {
            var get_set = frappe.model.get_doc("Maintenance System Settings")
            if(frm.doc.docstatus <1){
                frm.set_value("commission_based_on", get_set.commission_based_on)
                frm.set_value("company", get_set.comapny)
            }


        });
        frm.set_query("beneficiary", function() {
            return {
                "filters": {
                    "commission_enable": 1
                }
            };
        });
    },
    get_invoices: function(frm) {
        frappe.call({
            "method": "maintenance_system.maintenance_system.doctype.commission_payment.commission_payment.get_invoices",

            args: {
                team: frm.doc.beneficiary,
                commission:frm.doc.commission_based_on
            },
            callback: function (r) {
                frm.doc.table_6=[]
                var total_paid_amount=0.0;
                var commission_rate=0.0;
                $.each(r.message, function(i, d) {
                    var row = frappe.model.add_child(cur_frm.doc, "table_6");
                    row.maintenance_invoice = d.name;
                    row.date = d.posting_date;
                    row.mode_of_payment=d.payment_method
                    row.paid_amount=d.paid_amount
                    total_paid_amount+=d.paid_amount
                    if (frm.doc.commission_type_section == "Percentage"){
                        row.commission=0.0
                    }else if(frm.doc.commission_type_section == "Fixed Amount"){
                        row.commission=frm.doc.fixed_amount
                        commission_rate+=frm.doc.fixed_amount
                    }
                });
                frm.set_value("total_paid_amount",total_paid_amount)
                if (frm.doc.commission_type_section == "Percentage"){
                    frm.set_value("total_commission",total_paid_amount*frm.doc.percentage/100)
                }else if(frm.doc.commission_type_section == "Fixed Amount"){
                    frm.set_value("total_commission",commission_rate)
                }
                refresh_field("total_paid_amount");
                refresh_field("total_commission");
                refresh_field("table_6");	
            }
        });
    }

});
