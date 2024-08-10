frappe.listview_settings['Maintenance Directing'] = {
	add_fields: ["status"],
	get_indicator: function(doc) {
		if (doc.status === "In Processing"){
			return [__("In Processing"), "orange", "status,=,In Processing"];
		}
		else if (doc.status === "Paid") {
                        return [__("Paid"), "green", "status,=,Paid"];
                }
                else if (doc.status === "Unpaid") {
                        return [__("Unpaid"), "orange", "status,=,Unpaid"];
                }
                else if (doc.status === "Rejected") {
                    return [__("Rejected"), "red", "status,=,Rejected"];
            }
	}
};

