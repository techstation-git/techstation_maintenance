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
	return [_("Customer") + ":Link/Customer:120",
			_("Maintenance Item") + ":Link/Maintenance Item:150",
			_("Receive Maintenance Item") + ":Link/Receive Maintenance Item:220",
			_("Status") + ":Data:100"]

def get_data(conditions,filters):
	orders = frappe.db.sql("""select customer,maintenance_item,name,status 
				from `tabReceive Maintenance Item` where 
				docstatus = 1 %s order by creation asc;"""%conditions, filters, as_list=1)
	return orders

def get_conditions(filters):
	conditions = ""
	if filters.get("status"): conditions += "and status = %(status)s"
	if filters.get("customer"): conditions += "and customer = %(customer)s"
	if filters.get("maintenance_item"): conditions += "and maintenance_item = %(maintenance_item)s"

	return conditions, filters
