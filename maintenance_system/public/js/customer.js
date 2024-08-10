frappe.ui.form.on("Customer", {
    "onload": function (frm, cdt, cdn) {
        frappe.call({
            "method": "maintenance_system.maintenance_system.doctype.dashboard.getAmount",
            args: {
                customer: frm.doc.name
            },
            callback: function (r) {
                frm.dashboard.add_indicator(__('MS Total: {0}',
                    [format_currency(r.message[0][0], r.message[0][0].currency)]), 'blue');

                frm.dashboard.add_indicator(__('MS Outstanding: {0}',
                    [format_currency(r.message[0][1], r.message[0][0].currency)]), 'orange');

                frm.dashboard.add_indicator(__('MS Received: {0}',
                    [format_currency(r.message[0][0] - r.message[0][1], r.message[0][0].currency)]), 'green');
            }
        });
    }
});

frappe.ui.form.on("Customer", {
    before_save(frm) {
        // alert("Hello")
        // frappe.model.with_doc("Selling Settings", frm.doc.trigger, function () {
        //     var tabletransfer = frappe.model.get_doc("Selling Settings")
        //     if(tabletransfer.default_customer_type == ""){
        //         frappe.throw("Please Select a Default Customer Type")
        //     }else{
        //         frm.set_value("customer_type",tabletransfer.default_customer_type)
        //     }
            
        // });
    }

});


