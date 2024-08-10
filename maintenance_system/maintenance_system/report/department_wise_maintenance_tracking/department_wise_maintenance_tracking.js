// Copyright (c) 2016, Tech Station and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Department Wise Maintenance Tracking"] = {
	"filters": [
		{
                    "fieldname": "department",
                    "label": __("Department"),
                    "fieldtype": "Link",
                    "options": "Maintenance Department"
                }
	]
};
