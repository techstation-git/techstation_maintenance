frappe.listview_settings['Maintenance Order'] = {
    
        add_fields: ["status"],
        get_indicator: function(doc) {
                if (doc.status === "Waiting"){
                        return [__("Waiting"), "darkgrey", "status,=,Waiting"];
                }
                else if (doc.status === "In Processing") {
                        return [__("In Processing"), "orange", "status,=,In Processing"];
                }
		else if (doc.status === "Under Maintenance") {
                        return [__("Under Maintenance"), "black", "status,=,Under Maintenance"];
                }
		else if (doc.status === "Complete") {
                        return [__("Complete"), "green", "status,=,Complete"];
                }
		else if (doc.status === "Paid") {
                        return [__("Paid"), "green", "status,=,Paid"];
                }
                else if (doc.status === "Unpaid") {
                        return [__("Unpaid"), "orange", "status,=,Unpaid"];
                }
		else if (doc.status === "In Directing") {
                        return [__("In Directing"), "red", "status,=,In Directing"];
                }
                else if (doc.status === "Payment Received") {
                        return [__("Payment Received"), "green", "status,=,Payment Received"];
                }else if (doc.status === "Rejected") {
                    return [__("Rejected"), "red", "status,=,Rejected"];
            }
        }
};
