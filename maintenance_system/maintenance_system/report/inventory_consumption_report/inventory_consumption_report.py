import frappe
from frappe import _

def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data

def get_columns():
	return [
		{"label": _("Item Code"), "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 150},
		{"label": _("Item Name"), "fieldname": "item_name", "fieldtype": "Data", "width": 200},
		{"label": _("Total Consumed Qty"), "fieldname": "total_qty", "fieldtype": "Float", "width": 150},
		{"label": _("Average Qty per Order"), "fieldname": "avg_qty", "fieldtype": "Float", "width": 150},
		{"label": _("Total Cost"), "fieldname": "total_amount", "fieldtype": "Currency", "width": 150}
	]

def get_data(filters):
	conditions = ""
	if filters.get("from_date"):
		conditions += f" AND mo.issue_date >= '{filters['from_date']}'"
	if filters.get("to_date"):
		conditions += f" AND mo.issue_date <= '{filters['to_date']}'"

	return frappe.db.sql(f"""
		SELECT 
			moi.item_code,
			i.item_name,
			SUM(moi.qty) as total_qty,
			AVG(moi.qty) as avg_qty,
			SUM(moi.amount) as total_amount
		FROM `tabMaintenance Order Spare Parts` moi
		JOIN `tabMaintenance Order` mo ON moi.parent = mo.name
		JOIN `tabItem` i ON moi.item_code = i.name
		WHERE mo.docstatus = 1 {conditions}
		GROUP BY moi.item_code, i.item_name
		ORDER BY total_qty DESC
	""", as_dict=True)
