"""
Scheduled tasks for Maintenance System.
"""
from __future__ import unicode_literals
import frappe
from frappe.utils import now_datetime, add_to_date


def check_overdue_tickets():
    """
    Daily task: Send alert to Operations Manager users when a Maintenance Order
    has been in 'Waiting' or 'In Directing' status for more than 72 hours
    without any action.
    """
    cutoff = add_to_date(now_datetime(), hours=-72)

    overdue_orders = frappe.db.sql("""
        SELECT name, customer, issue_date, status, maintenance_order_added_by
        FROM `tabMaintenance Order`
        WHERE docstatus = 1
          AND status IN ('Waiting', 'In Directing')
          AND creation <= %s
    """, (cutoff,), as_dict=True)

    if not overdue_orders:
        return

    # Get all users with Operations Officer or Maintenance Manager roles
    manager_users = frappe.db.sql("""
        SELECT DISTINCT u.name, u.email
        FROM `tabUser` u
        JOIN `tabHas Role` hr ON hr.parent = u.name
        WHERE hr.role IN ('Operations Officer', 'Maintenance Manager')
          AND u.enabled = 1
          AND u.email NOT LIKE '%@example.com'
    """, as_dict=True)

    if not manager_users:
        return

    order_list_html = "".join([
        f"<li><b>{o.name}</b> – Customer: {o.customer} | Status: {o.status} | Created: {o.issue_date}</li>"
        for o in overdue_orders
    ])

    for user in manager_users:
        if not user.email:
            continue
        frappe.sendmail(
            recipients=[user.email],
            subject=f"⚠️ {len(overdue_orders)} Overdue Maintenance Ticket(s) – Action Required",
            message=f"""
            <p>Dear {user.name},</p>
            <p>The following maintenance orders have been open for more than <b>72 hours</b> without progress:</p>
            <ul>{order_list_html}</ul>
            <p>Please review and assign technicians to these tickets immediately.</p>
            <p>— Maintenance System Automated Alert</p>
            """
        )

    frappe.logger().info(
        f"[Maintenance System] Sent overdue ticket alert: {len(overdue_orders)} tickets to {len(manager_users)} managers"
    )
