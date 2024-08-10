from __future__ import unicode_literals
import frappe
from frappe.model.document import Document


@frappe.whitelist(allow_guest=True)
def getContact(customer,app_name):
	d = frappe.get_installed_apps()
	if app_name in d:
		item_data = frappe.db.sql("""select con.preferred_method_of_communication,con.phone,con.mobile_no,con.mobile_no_1,
		con.mobile_no_2,con.mobile_no_3,con.whatsapp,con.telegram from `tabDynamic Link` dl, `tabContact` con 
		where dl.parent = con.name and dl.link_doctype = 'Customer' and dl.link_name = '{0}';""".format(customer), as_list=1)
		return item_data

