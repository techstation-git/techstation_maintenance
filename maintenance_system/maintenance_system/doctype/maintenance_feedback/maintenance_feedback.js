// Copyright (c) 2020, Tech Station and contributors
// For license information, please see license.txt

frappe.ui.form.on('Maintenance Feedback', {
	bad: function(frm) {
		frm.set_value("good",0);
		frm.set_value("excellent",0);
		frm.set_df_property('feedback',  'reqd', 1);
	},

	good: function(frm) {
                frm.set_value("bad",0);
                frm.set_value("excellent",0);
		frm.set_df_property('feedback',  'reqd', 0);
        },

	excellent: function(frm) {
                frm.set_value("bad",0);
                frm.set_value("good",0);
		frm.set_df_property('feedback',  'reqd', 0);
        }
});
