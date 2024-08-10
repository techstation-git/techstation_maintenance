// Copyright (c) 2020, Tech Station and contributors
// For license information, please see license.txt

frappe.ui.form.on('Maintenance Schedule List', {
	order_type: function(frm) {
		if(frm.doc.order_type == "Internal"){
			frm.set_value("type","Internal");
			frm.set_df_property('days',  'reqd', 1);
			frm.set_df_property('territory',  'reqd', 0);
		}
		if(frm.doc.order_type == "External"){
			frm.set_value("type","External");
                        frm.set_df_property('days',  'reqd', 0);
                        frm.set_df_property('territory',  'reqd', 1);
                }
	}
});
