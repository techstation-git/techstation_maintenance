from __future__ import unicode_literals
import frappe
from frappe.model.document import Document


@frappe.whitelist(allow_guest=True)
def getAddress(customer,app_name):
	d = frappe.get_installed_apps()
	if app_name in d:
		item_data = frappe.db.sql("""select adr.address_line1,adr.city,adr.street,adr.country,adr.pincode,adr.house_number,
			adr.apartment_number,adr.floor,adr.way_to_climb,adr.special_marque 
			from `tabDynamic Link` dl, `tabAddress` adr where dl.parent = adr.name and dl.link_doctype = 'Customer' 
			and dl.link_name = '{0}';""".format(customer), as_list=1)
		return item_data
