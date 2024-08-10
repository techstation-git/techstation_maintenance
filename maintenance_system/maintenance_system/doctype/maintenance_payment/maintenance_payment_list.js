frappe.listview_settings['Maintenance Payment'] = {
	add_fields: ["status"],
	get_indicator: function(doc) {
		if (doc.status === "Draft"){
			return [__("Draft"), "red", "status,=,Draft"];
		}
		else if (doc.status === "Balance Available") {
                        return [__("Balance Available"), "orange", "status,=,Balance Available"];
                }
		else if (doc.status === "Allocated") {
                        return [__("Allocated"), "green", "status,=,Allocated"];
                }
	}
};


