# Copyright (c) 2026, Tech Station and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {
            "fieldname": "technician_custody",
            "label": _("Custody Record"),
            "fieldtype": "Link",
            "options": "Technician Custody",
            "width": 150
        },
        {
            "fieldname": "maintenance_team",
            "label": _("Maintenance Team"),
            "fieldtype": "Link",
            "options": "Maintenance Team",
            "width": 150
        },
        {
            "fieldname": "maintenance_order",
            "label": _("Maintenance Order"),
            "fieldtype": "Link",
            "options": "Maintenance Order",
            "width": 150
        },
        {
            "fieldname": "item_code",
            "label": _("Item Code"),
            "fieldtype": "Link",
            "options": "Item",
            "width": 120
        },
        {
            "fieldname": "item_name",
            "label": _("Item Name"),
            "fieldtype": "Data",
            "width": 150
        },
        {
            "fieldname": "qty_issued",
            "label": _("Qty Issued"),
            "fieldtype": "Float",
            "width": 100
        },
        {
            "fieldname": "qty_returned",
            "label": _("Qty Returned"),
            "fieldtype": "Float",
            "width": 100
        },
        {
            "fieldname": "outstanding_qty",
            "label": _("Outstanding Qty"),
            "fieldtype": "Float",
            "width": 120
        },
        {
            "fieldname": "status",
            "label": _("Status"),
            "fieldtype": "Data",
            "width": 100
        },
        {
            "fieldname": "expected_return_date",
            "label": _("Expected Return Date"),
            "fieldtype": "Date",
            "width": 120
        }
    ]

def get_data(filters):
    conditions = ""
    if filters.get("maintenance_team"):
        conditions += " AND tc.maintenance_team = %(maintenance_team)s"
    
    if filters.get("item_code"):
        conditions += " AND ci.item_code = %(item_code)s"
        
    if filters.get("from_date") and filters.get("to_date"):
        conditions += " AND (tc.creation BETWEEN %(from_date)s AND %(to_date)s)"

    # Status filter logic needs create temporary table or smart query
    # Simple check for now: 
    # If status filter is 'Issued', we want outstanding > 0
    # If status filter is 'Return', we want outstanding == 0
    
    status_condition = ""
    if filters.get("status"):
        if filters.get("status") == "Issued":
            status_condition = "HAVING outstanding_qty > 0"
        elif filters.get("status") == "Returned":
            status_condition = "HAVING outstanding_qty <= 0"

    sql = """
        SELECT
            tc.name as technician_custody,
            tc.maintenance_team,
            tc.maintenance_order,
            ci.item_code,
            ci.item_name,
            ci.qty_issued,
            ci.qty_returned,
            (ci.qty_issued - ci.qty_returned) as outstanding_qty,
            tc.custody_status as status,
            tc.expected_return_date
        FROM
            `tabTechnician Custody` tc
        JOIN
            `tabCustody Item` ci on ci.parent = tc.name
        WHERE
            tc.docstatus = 1
            {conditions}
        {status_condition}
        ORDER BY
            tc.creation DESC
    """.format(conditions=conditions, status_condition=status_condition)

    return frappe.db.sql(sql, filters, as_dict=1)
