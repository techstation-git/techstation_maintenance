frappe.listview_settings['External Processing'] = {
	add_fields: ["status"],
	get_indicator: function(doc) {
		if (doc.status === "Draft"){
			return [__("Draft"), "red", "status,=,Draft"];
		}
		else if (doc.status === "Start") {
                        return [__("Start"), "purple", "status,=,Start"];
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
		else if (doc.status === "Delivered") {
                        return [__("Delivered"), "yellow", "status,=,Delivered"];
                }
        else if (doc.status === "Rejected") {
                    return [__("Rejected"), "red", "status,=,Rejected"];
            }
	}
};


