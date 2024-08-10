// Copyright (c) 2016, Tech Station and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Maintenance Received Item Summery"] = {
	"filters": [
		{
                    "fieldname": "status",
                    "label": __("Status"),
                    "fieldtype": "Select",
                    "options": "\nOccupied\nAvailable",
                },
		{
                    "fieldname": "customer",
                    "label": __("Customer"),
                    "fieldtype": "Link",
                    "options": "Customer",
                },
		{
                    "fieldname": "maintenance_item",
                    "label": __("Maintenance Item"),
                    "fieldtype": "Link",
                    "options": "Maintenance Item",
                }
	]
};
