frappe.listview_settings['Maintenance Material Receipt'] = {
	add_fields: ["status"],
	get_indicator: function(doc) {
		if (doc.status === "Delivered"){
			return [__("Delivered"), "yellow", "status,=,Delivered"];
		}
		else if (doc.status === "Unpaid") {
                        return [__("Unpaid"), "orange", "status,=,Unpaid"];
                }
		else if (doc.status === "Paid") {
                        return [__("Paid"), "green", "status,=,Paid"];
                }
	}
};
