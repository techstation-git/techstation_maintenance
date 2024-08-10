// Copyright (c) 2016, Tech Station and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Maintenance Revenue Collection"] = {
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
                    "fieldname": "customer",
                    "label": __("Customer"),
                    "fieldtype": "Link",
                    "options": "Customer",
                }
	]
};
