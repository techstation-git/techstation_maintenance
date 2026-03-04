# Copyright (c) 2026, Tech Station and contributors
# Maintenance Order event notifications

import frappe
from frappe.utils import getdate, now_datetime, add_days


def on_maintenance_order_submit(doc, method):
    """Send notification to Sales Person when Maintenance Order is submitted."""
    _notify_sales_person(doc, "New Maintenance Order",
        f"A new maintenance order {doc.name} has been created for customer {doc.customer_name}.\n\n"
        f"Item: {doc.maintenance_item}\nStatus: {doc.status}\nIssue Date: {doc.issue_date}"
    )


def on_maintenance_order_update(doc, method):
    """Send notification when Maintenance Order status changes to Complete."""
    if doc.status == "Complete":
        _notify_sales_person(doc, f"Maintenance Order Completed: {doc.name}",
            f"Maintenance order {doc.name} for customer {doc.customer_name} has been completed.\n\n"
            f"Item: {doc.maintenance_item}\nCompletion Date: {doc.maintenance_end_date}"
        )


def _notify_sales_person(doc, subject, message):
    """Helper to send email/system notification to the assigned sales person."""
    sales_person = doc.get("sales_person")
    if not sales_person:
        return

    employee_email = frappe.db.get_value("Employee", sales_person, "prefered_email") or \
                     frappe.db.get_value("Employee", sales_person, "company_email") or \
                     frappe.db.get_value("Employee", sales_person, "personal_email")

    if not employee_email:
        return

    try:
        frappe.sendmail(
            recipients=[employee_email],
            subject=subject,
            message=message,
            reference_doctype=doc.doctype,
            reference_name=doc.name,
        )
    except Exception as e:
        frappe.log_error(f"Failed to notify sales person for {doc.name}: {e}", "Maintenance Notification")


@frappe.whitelist()
def send_72hr_overdue_alerts():
    """
    Scheduled task: Check orders inactive for more than 72 hours and alert Operations Manager.
    Wire in scheduler_events in hooks.py.
    """
    threshold = add_days(now_datetime(), -3)
    overdue_orders = frappe.db.sql("""
        SELECT name, customer, customer_name, maintenance_item, status, modified
        FROM `tabMaintenance Order`
        WHERE docstatus = 1
          AND status IN ('Waiting', 'In Directing', 'Under Maintenance')
          AND modified < %s
    """, threshold, as_dict=True)

    if not overdue_orders:
        return

    managers = frappe.get_all("Has Role", filters={"role": "Maintenance Manager"}, fields=["parent"])
    manager_emails = []
    for m in managers:
        email = frappe.db.get_value("User", m.parent, "email")
        if email and email != "Administrator":
            manager_emails.append(email)

    if not manager_emails:
        return

    rows = "".join([
        f"<tr><td>{o.name}</td><td>{o.customer_name}</td><td>{o.maintenance_item}</td>"
        f"<td>{o.status}</td><td>{str(o.modified)[:16]}</td></tr>"
        for o in overdue_orders
    ])

    html = f"""
    <p>The following Maintenance Orders have had NO activity for more than 72 hours:</p>
    <table border="1" cellpadding="6" style="border-collapse:collapse">
        <thead>
            <tr><th>Order</th><th>Customer</th><th>Item</th><th>Status</th><th>Last Modified</th></tr>
        </thead>
        <tbody>{rows}</tbody>
    </table>
    <p>Please take action to move these orders forward.</p>
    """

    frappe.sendmail(
        recipients=manager_emails,
        subject=f"⏰ {len(overdue_orders)} Maintenance Order(s) Overdue (72h+ no action)",
        message=html,
    )
