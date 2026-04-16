import frappe
from erpnext.accounts.doctype.sales_invoice.sales_invoice import SalesInvoice


class SalesInvoice(SalesInvoice):
	def on_cancel(self):
		super().on_cancel()
		self.ignore_linked_doctypes = (
			"GL Entry",
			"Stock Ledger Entry",
			"Repost Item Valuation",
			"Repost Payment Ledger",
			"Repost Payment Ledger Items",
			"Payment Ledger Entry",
		)
		get_items = frappe.db.sql(
			"""
			select name from `tabMaintenance Item`
			where sales_invoice = %s and warranty_status = 'Enabled'
			""",
			(self.name,),
		)
		if get_items:
			for row in get_items:
				frappe.db.set_value("Maintenance Item", row[0], "warranty_status", "")
        


@frappe.whitelist()
def create_maintenance_item(invoice):
    if invoice:
        get_invoice=frappe.get_doc("Sales Invoice",invoice)
        if get_invoice.get("items"):
            for item in get_invoice.get("items"):
                warranty_status,warranty_template,maintenance_categorie=frappe.db.get_value("Item",{"item_code":item.item_code},["warranty_status","warranty_template","maintenance_categories"])
                maintenance_item=frappe.new_doc("Maintenance Item")
                maintenance_item.customer=get_invoice.get("customer")
                maintenance_item.item=item.item_code
                if warranty_status == "Enabled":
                    maintenance_item.warranty_status=warranty_status
                    maintenance_item.warranty_template=warranty_template
                    maintenance_item.warranty_start_date=get_invoice.get("posting_date")
                    maintenance_item.maintenance_categories=maintenance_categorie
                maintenance_item.sales_invoice=get_invoice.get("name")
                maintenance_item.item_sold_by_us=1
                maintenance_item.flags.ignore_mandatory=True
                maintenance_item.save()
                maintenance_item.submit()
                frappe.db.set_value("Sales Invoice",get_invoice.get("name"),"warranty_created",1)
                # frappe.msgprint("Maintenance Item Created Successfully")
        return "Maintenance Item Created Successfully"
