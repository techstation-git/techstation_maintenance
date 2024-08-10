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
	return [_("Date") + ":Date:120",
			_("Maintenance Order") + ":Link/Maintenance Order:150",
			_("Maintenance Directing") + ":Link/Maintenance Directing:180",
			_("Maintenance Invoice") + ":Link/Maintenance Invoice:150",
			_("Customer") + ":Link/Customer:150",
			_("Grand Total") + ":Currency:150",
			_("Advance Paid") + ":Currency:150",
			_("Outstanding Amount") + ":Currency:150"]

def get_data(conditions,filters):
	orders = frappe.db.sql("""select posting_date,maintenance_order,maintenance_directing,name as "Maintenance Invoice",
				customer, rounded_total, advance_amount, outstanding_amount from `tabMaintenance Invoice` where 
				docstatus = 1 and status = 'Unpaid' %s order by posting_date asc;"""%conditions, filters, as_list=1)
	return orders

def get_conditions(filters):
	conditions = ""
	if filters.get("from_date"): conditions += " and posting_date >= %(from_date)s"
	if filters.get("to_date"): conditions += " and posting_date <= %(to_date)s"
	if filters.get("customer"): conditions += "and customer = %(customer)s"

	return conditions, filters


