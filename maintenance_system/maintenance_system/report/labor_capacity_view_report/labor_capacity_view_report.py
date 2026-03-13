# Copyright (c) 2026, Tech Station and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data

def get_columns():
	return [
		{
			"label": _("Specialty / Department"),
			"fieldname": "specialty",
			"fieldtype": "Data",
			"width": 200
		},
		{
			"label": _("Active Maintenance Orders"),
			"fieldname": "active_orders",
			"fieldtype": "Int",
			"width": 180
		},
		{
			"label": _("Available Technicians"),
			"fieldname": "available_technicians",
			"fieldtype": "Int",
			"width": 180
		},
		{
			"label": _("Capacity Gap"),
			"fieldname": "capacity_gap",
			"fieldtype": "Int",
			"width": 150
		}
	]

def get_data(filters):
	# 1. Get Specializations
	specializations = frappe.get_all("Employee Specialization", fields=["specialty"], distinct=True)
	specialties = [s.specialty for s in specializations if s.specialty]
	
	if not specialties:
		# Fallback to some defaults if none found in DB
		specialties = ["Electrical", "Plumbing", "HVAC", "Carpentry", "Mechanical", "IT / Networking", "Painting", "Civil Works"]

	# 2. Get Active Orders Counts per Department
	# Mapping assumption: Department Name matches Specialty Name
	order_counts = frappe.db.sql("""
		SELECT 
			maintenance_department as specialty, 
			COUNT(name) as count
		FROM 
			`tabMaintenance Order`
		WHERE 
			docstatus < 2 
			AND status NOT IN ('Complete', 'Cancelled', 'Rejected')
		GROUP BY 
			maintenance_department
	""", as_dict=True)

	order_map = {d.specialty: d.count for d in order_counts if d.specialty}

	# 3. Get Employee Counts per Specialty
	# Employees have a table 'specializations' linking to 'Employee Specialization'
	emp_counts = frappe.db.sql("""
		SELECT 
			child.specialty, 
			COUNT(DISTINCT parent.name) as count
		FROM 
			`tabEmployee Specialization` child
		JOIN 
			`tabEmployee` parent ON child.parent = parent.name
		WHERE 
			parent.status = 'Active'
		GROUP BY 
			child.specialty
	""", as_dict=True)

	emp_map = {d.specialty: d.count for d in emp_counts if d.specialty}

	# 4. Combine Data
	data = []
	all_keys = set(list(order_map.keys()) + list(emp_map.keys()) + specialties)
	
	for key in sorted(all_keys):
		orders = order_map.get(key, 0)
		technicians = emp_map.get(key, 0)
		gap = technicians - orders
		
		data.append({
			"specialty": key,
			"active_orders": orders,
			"available_technicians": technicians,
			"capacity_gap": gap
		})

	return data
