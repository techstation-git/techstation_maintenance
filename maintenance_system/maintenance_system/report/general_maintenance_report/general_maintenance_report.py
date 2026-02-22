import frappe
from frappe import _

def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data

def get_columns():
	return [
		{"label": _("ID"), "fieldname": "name", "fieldtype": "Link", "options": "Maintenance Order", "width": 120},
		{"label": _("Customer"), "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 120},
		{"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 100},
		{"label": _("Type"), "fieldname": "ticket_type", "fieldtype": "Link", "options": "Maintenance Ticket Type", "width": 120},
		{"label": _("Date"), "fieldname": "issue_date", "fieldtype": "Date", "width": 100},
		{"label": _("Total Amount"), "fieldname": "total_amount", "fieldtype": "Currency", "width": 120},
		{"label": _("Outstanding"), "fieldname": "outstanding_amount", "fieldtype": "Currency", "width": 120}
	]

def get_data(filters):
	conditions = ""
	if filters.get("from_date"):
		conditions += f" AND issue_date >= '{filters['from_date']}'"
	if filters.get("to_date"):
		conditions += f" AND issue_date <= '{filters['to_date']}'"
	if filters.get("ticket_type"):
		conditions += f" AND ticket_type = '{filters['ticket_type']}'"

	return frappe.db.sql(f"""
		SELECT name, customer, status, ticket_type, issue_date, total_amount, outstanding_amount
		FROM `tabMaintenance Order`
		WHERE docstatus < 2 {conditions}
		ORDER BY issue_date DESC
	""", as_dict=True)
