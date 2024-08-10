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
			_("Maintenance Invoice") + ":Link/Maintenance Invoice:150",
			_("Invoice Date") + ":Date:130",
			_("Bad") + ":Check:70",
			_("Good") + ":Check:70",
			_("Excellent") + ":Check:90",
			_("Feedback") + ":Text:150"]

def get_data(conditions,filters):
	orders = frappe.db.sql("""select customer,invoice_number,invoice_date,bad,good,excellent,feedback 
				from `tabMaintenance Feedback` where 
				docstatus = 1 %s order by invoice_date asc;"""%conditions, filters, as_list=1)
	return orders

def get_conditions(filters):
	conditions = ""
	if filters.get("customer"): conditions += "and customer = %(customer)s"

	return conditions, filters
