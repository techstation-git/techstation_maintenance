frappe.listview_settings['Maintenance Invoice'] = {
	add_fields: ["status"],
	get_indicator: function(doc) {
		if (doc.status === "Unpaid"){
			return [__("Unpaid"), "orange", "status,=,Unpaid"];
		}
		else if (doc.status === "Paid") {
                        return [__("Paid"), "green", "status,=,Paid"];
                }
		else if (doc.status === "Partly Paid") {
                        return [__("Partly Paid"), "yellow", "status,=,Partly Paid"];
                }
	}
};


