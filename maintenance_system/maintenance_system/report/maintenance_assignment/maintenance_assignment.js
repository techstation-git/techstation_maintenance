// Copyright (c) 2016, Tech Station and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Maintenance Assignment"] = {
	"filters": [
		{
        	    "fieldname": "from_date",
       		    "label": __("From Date"),
        	    "fieldtype": "Date",
		    "default": frappe.datetime.month_start()
        	},
		{
        	    "fieldname": "to_date",
        	    "label": __("To Date"),
        	    "fieldtype": "Date",
		    "default": frappe.datetime.month_end()
        	},
		{
                    "fieldname": "territory",
                    "label": __("Territory"),
                    "fieldtype": "Link",
                    "options": "Territory"
                },
		{
                    "fieldname": "customer",
                    "label": __("Customer"),
                    "fieldtype": "Link",
                    "options": "Customer"
                },
		{
                    "fieldname": "type",
                    "label": __("Type"),
                    "fieldtype": "Select",
                    "options": "\nInternal\nExternal"
                },
		{
                    "fieldname": "department",
                    "label": __("Department"),
                    "fieldtype": "Link",
                    "options": "Maintenance Department"
                },
		{
                    "fieldname": "team",
                    "label": __("Team"),
                    "fieldtype": "Link",
                    "options": "Maintenance Team"
                },
		{
                    "fieldname": "car",
                    "label": __("Car"),
                    "fieldtype": "Link",
                    "options": "Maintenance Support Car"
                }
	]
};
