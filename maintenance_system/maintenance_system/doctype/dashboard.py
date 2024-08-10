from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

@frappe.whitelist(allow_guest=True)
def getAmount(customer):
	mt = frappe.db.sql("""select sum(rounded_total),sum(outstanding_amount) from `tabMaintenance Invoice` where 
				docstatus = 1 and customer = %s;""",(customer),as_list=1)
	return mt if mt else ""

