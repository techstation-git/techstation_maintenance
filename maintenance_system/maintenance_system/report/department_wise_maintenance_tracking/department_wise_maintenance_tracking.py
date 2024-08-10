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
			_("Issue Date") + ":Date:150",
			_("Maintenance End Date") + ":Date:150",
			_("Maintenance Item") + ":Link/Maintenance Item:150",
			_("Receive Maintenance Item") + ":Link/Receive Maintenance Item:220",
			_("Status") + ":Data:100",
			_("Maintenance Department") + ":Link/Maintenance Department:150",
			_("Time Status") + ":Data:150"]

def get_data(conditions,filters):
	orders = frappe.db.sql("""select customer,issue_date,maintenance_end_date,maintenance_item,receive_maintenance_items,
				status,maintenance_department,
				IF((CURDATE() > maintenance_end_date) and status = "In Processing", "Timeline Crossed", "Under Timeline")
				 from `tabMaintenance Directing` where
				docstatus = 1 %s order by issue_date asc;"""%conditions, filters, as_list=1)
	return orders

def get_conditions(filters):
	conditions = ""
	if filters.get("department"): conditions += "and maintenance_department = %(department)s"

	return conditions, filters
