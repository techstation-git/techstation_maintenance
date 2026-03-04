# Copyright (c) 2026, Tech Station and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt


class MaintenanceOrder(Document):
    pass


@frappe.whitelist()
def calculate_technician_bonuses(maintenance_order):
    """Calculate bonuses for all technicians on a maintenance order."""
    mo = frappe.get_doc("Maintenance Order", maintenance_order)

    # Get invoice value for percentage-based calculation
    invoice_value = flt(mo.net_total) or flt(mo.total_amount) or 0
    material_cost = flt(mo.total) or 0  # spare parts total
    net_value = max(invoice_value - material_cost, 0)

    bonuses = []
    team_table = frappe.get_all(
        "Maintenance Team Table",
        filters={"parent": maintenance_order, "parenttype": "Maintenance Order"},
        fields=["team"]
    )

    for row in team_table:
        team = frappe.get_doc("Maintenance Team", row.team)
        # Try to get the user's Employee record
        employee = frappe.db.get_value("Employee", {"user_id": team.user}, "name") if hasattr(team, "user") else None
        if not employee:
            continue

        emp = frappe.get_doc("Employee", employee)
        technician_type_name = emp.get("technician_type")
        if not technician_type_name:
            continue

        tech_type = frappe.get_doc("Technician Type", technician_type_name)
        bonus_amount = 0
        operations_count = 1  # default

        if tech_type.bonus_method == "Fixed Amount per Operation":
            bonus_amount = flt(tech_type.fixed_amount) * operations_count
        elif tech_type.bonus_method == "Percentage of Net Value":
            bonus_amount = net_value * (flt(tech_type.percentage) / 100)

        bonuses.append({
            "employee": employee,
            "employee_name": emp.employee_name,
            "technician_type": technician_type_name,
            "bonus_method": tech_type.bonus_method,
            "bonus_amount": bonus_amount
        })

    return bonuses
