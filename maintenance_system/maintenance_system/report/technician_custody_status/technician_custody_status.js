// Copyright (c) 2026, Tech Station and contributors
// For license information, please see license.txt

frappe.query_reports["Technician Custody Status"] = {
    "filters": [
        {
            "fieldname": "maintenance_team",
            "label": __("Maintenance Team"),
            "fieldtype": "Link",
            "options": "Maintenance Team",
            "reqd": 0
        },
        {
            "fieldname": "item_code",
            "label": __("Item"),
            "fieldtype": "Link",
            "options": "Item",
            "reqd": 0
        },
        {
            "fieldname": "status",
            "label": __("Status"),
            "fieldtype": "Select",
            "options": ["", "Issued", "Returned"],
            "default": "",
            "reqd": 0
        },
        {
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
            "reqd": 0
        },
        {
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.get_today(),
            "reqd": 0
        }
    ]
};
