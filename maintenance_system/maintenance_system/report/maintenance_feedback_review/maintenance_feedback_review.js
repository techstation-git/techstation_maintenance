// Copyright (c) 2016, Tech Station and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Maintenance Feedback Review"] = {
	"filters": [
		{
                    "fieldname": "customer",
                    "label": __("Customer"),
                    "fieldtype": "Link",
                    "options": "Customer",
                }
	]
};
