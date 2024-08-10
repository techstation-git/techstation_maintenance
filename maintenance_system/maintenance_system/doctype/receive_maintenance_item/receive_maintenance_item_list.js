frappe.listview_settings['Receive Maintenance Item'] = {
	add_fields: ["status"],
	get_indicator: function(doc) {
		if (doc.status === "Draft"){
			return [__("Draft"), "red", "status,=,Draft"];
		}
		else if (doc.status === "Available") {
                        return [__("Available"), "green", "status,=,Available"];
                }
		else if (doc.status === "Occupied") {
                        return [__("Occupied"), "darkgrey", "status,=,Occupied"];
                }
	}
};

