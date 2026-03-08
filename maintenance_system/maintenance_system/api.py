# Copyright (c) 2026, Tech Station and contributors
# Whitelisted API endpoints for the Operations Dashboard

import frappe
from frappe.utils import add_days, now_datetime, get_first_day, get_last_day, today


@frappe.whitelist()
def get_dashboard_data():
    """Single endpoint that returns all data needed for the Operations Dashboard."""

    # 1. Status breakdown (active orders)
    status_counts = frappe.db.sql("""
        SELECT status, COUNT(name) as cnt
        FROM `tabMaintenance Order`
        WHERE docstatus = 1
        GROUP BY status
    """, as_dict=True)

    # 2. Pending custody returns
    pending_custody = frappe.db.sql("""
        SELECT
            tc.name,
            tc.maintenance_order,
            tc.status as custody_status,
            tc.issue_date as expected_return_date
        FROM `tabTechnician Custody` tc
        WHERE tc.docstatus = 1
          AND tc.status IN ('Issued', 'Partially Returned', 'Overdue')
        ORDER BY tc.issue_date ASC
        LIMIT 50
    """, as_dict=True)

    # 3. Completed this month
    month_start = get_first_day(today())
    month_end = get_last_day(today())
    completed_this_month = frappe.db.count("Maintenance Order", {
        "docstatus": 1,
        "status": "Complete",
        "modified": ["between", [month_start, month_end]]
    })

    # 4. Overdue (72h no activity)
    threshold = add_days(now_datetime(), -3)
    overdue_count = frappe.db.count("Maintenance Order", {
        "docstatus": 1,
        "status": ["in", ["Waiting", "In Directing", "Under Maintenance"]],
        "modified": ["<", threshold]
    })

    # 5. Month name for display
    import datetime
    month_name = datetime.date.today().strftime("%B %Y")

    return {
        "status_counts": status_counts,
        "pending_custody": pending_custody,
        "completed_this_month": completed_this_month,
        "overdue_count": overdue_count,
        "month_name": month_name,
    }
