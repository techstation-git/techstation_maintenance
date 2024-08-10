# Copyright (c) 2013, Tech Station and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import msgprint, _

def execute(filters=None):
	conditions, filters = get_conditions(filters)
	columns = get_column()
	data = get_data(conditions,filters)
	return columns,data

def get_column():
	return [_("Issue Date") + ":Date:120",
			_("Maintenance Directing") + ":Link/Maintenance Directing:150",
			_("Customer") + ":Link/Customer:180",
			_("Territory") + ":Link/Territory:150",
			_("Maintenance Department") + ":Link/Maintenance Department:210",
			_("Maintenance Team") + ":Link/Maintenance Team:150",
			_("Maintenance Car") + ":Link/Maintenance Support Car:150",
			_("Order Type") + ":Data:150"]

def get_data(conditions,filters):
	orders = frappe.db.sql("""select issue_date,name,customer,territory,maintenance_department,maintenance_team,
				maintenance_support_car,order_type from `tabMaintenance Directing` where 
				docstatus = 1 %s order by issue_date asc;"""%conditions, filters, as_list=1)
	return orders

def get_conditions(filters):
	conditions = ""
	if filters.get("from_date"): conditions += " and issue_date >= %(from_date)s"
	if filters.get("to_date"): conditions += " and issue_date <= %(to_date)s"
	if filters.get("customer"): conditions += "and customer = %(customer)s"
	if filters.get("territory"): conditions += "and territory = %(territory)s"
	if filters.get("type"): conditions += "and order_type = %(type)s"
	if filters.get("department"): conditions += "and maintenance_department = %(department)s"
	if filters.get("team"): conditions += "and maintenance_team = %(team)s"
	if filters.get("car"): conditions += "and maintenance_support_car = %(car)s"

	return conditions, filters
