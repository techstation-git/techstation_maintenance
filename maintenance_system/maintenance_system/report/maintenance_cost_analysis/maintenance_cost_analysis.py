import frappe
from frappe import _

def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data

def get_columns():
	return [
		{"label": _("Order"), "fieldname": "name", "fieldtype": "Link", "options": "Maintenance Order", "width": 120},
		{"label": _("Customer"), "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 120},
		{"label": _("Revenue (Total)"), "fieldname": "total_amount", "fieldtype": "Currency", "width": 120},
		{"label": _("Material Cost"), "fieldname": "material_cost", "fieldtype": "Currency", "width": 120},
		{"label": _("Worker Rewards"), "fieldname": "rewards_total", "fieldtype": "Currency", "width": 120},
		{"label": _("Operational Misc Costs"), "fieldname": "misc_costs", "fieldtype": "Currency", "width": 120},
		{"label": _("Net Profit"), "fieldname": "net_profit", "fieldtype": "Currency", "width": 120}
	]

def get_data(filters):
	conditions = ""
	if filters.get("from_date"):
		conditions += f" AND mo.issue_date >= '{filters['from_date']}'"
	if filters.get("to_date"):
		conditions += f" AND mo.issue_date <= '{filters['to_date']}'"

	# Subqueries for sums of child tables
	return frappe.db.sql(f"""
		SELECT 
			mo.name,
			mo.customer,
			mo.total_amount,
			mo.total as material_cost,
			(SELECT SUM(calculated_reward) FROM `tabMaintenance Assignment` WHERE parent = mo.name) as rewards_total,
			(SELECT SUM(amount) FROM `tabMaintenance Cost` WHERE parent = mo.name) as misc_costs,
			(mo.total_amount 
				- IFNULL(mo.total, 0) 
				- IFNULL((SELECT SUM(calculated_reward) FROM `tabMaintenance Assignment` WHERE parent = mo.name), 0)
				- IFNULL((SELECT SUM(amount) FROM `tabMaintenance Cost` WHERE parent = mo.name), 0)
			) as net_profit
		FROM `tabMaintenance Order` mo
		WHERE mo.docstatus = 1 {conditions}
		ORDER BY mo.issue_date DESC
	""", as_dict=True)
