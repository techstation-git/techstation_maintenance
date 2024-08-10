frappe.ui.form.on('Item',  {
    warranty_status: function(frm) {
        if(frm.doc.warranty_status == "Enabled"){
        	frm.set_df_property('warranty_template',  'reqd',  1);
		frm.set_df_property('warranty_template',  'hidden',  0);
	}
	if(frm.doc.warranty_status != "Enabled"){
        	frm.set_df_property('warranty_template',  'reqd',  0);
		frm.set_df_property('warranty_template',  'hidden',  1);
	}
}
});

frappe.ui.form.on('Item',  {
    onload: function(frm) {
        if(frm.doc.warranty_status == "Enabled"){
                frm.set_df_property('warranty_template',  'reqd',  1);
		frm.set_df_property('warranty_template',  'hidden',  0);
        }
        if(frm.doc.warranty_status != "Enabled"){
                frm.set_df_property('warranty_template',  'reqd',  0);
		frm.set_df_property('warranty_template',  'hidden',  1);
        }
}
});
