"""
Scheduled tasks for Maintenance System.
"""
from __future__ import unicode_literals
import frappe
from frappe.utils import now_datetime, add_to_date

def check_overdue_tickets():
    """
    Hourly task: Send alert to Operations Officer users 
    when a Maintenance Order has been in 'Waiting' or 'In Directing' 
    status for more than 72 hours without being started.
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

    # Get all users with Operations Officer role
    ops_officers = frappe.db.sql("""
        SELECT DISTINCT u.name, u.email
        FROM `tabUser` u
        JOIN `tabHas Role` hr ON hr.parent = u.name
        WHERE hr.role = 'Operations Officer'
          AND u.enabled = 1
    """, as_dict=True)

    if not ops_officers:
        frappe.logger().warning("[Maintenance System] No Operations Officers found to notify about overdue tickets.")
        return

    order_list_html = "".join([
        f"<li><b>{o.name}</b> – Customer: {o.customer} | Status: {o.status} | Created: {o.issue_date}</li>"
        for o in overdue_orders
    ])

    for user in ops_officers:
        if not user.email:
            continue
        frappe.sendmail(
            recipients=[user.email],
            subject=f"🚨 URGENT: {len(overdue_orders)} Unstarted Maintenance Orders (72h+ Overdue)",
            message=f"""
            <p>Dear {user.name},</p>
            <p>The following maintenance orders have remained <b>unstarted</b> for more than <b>72 hours</b>:</p>
            <ul>{order_list_html}</ul>
            <p>Please take immediate action to assign and start these orders.</p>
            <hr>
            <p><small>This is an automated priority alert from the Maintenance System.</small></p>
            """
        )

    frappe.logger().info(
        f"[Maintenance System] Sent overdue ticket alert to Operations Officers: {len(overdue_orders)} tickets"
    )
