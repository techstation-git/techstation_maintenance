import frappe
from erpnext.accounts.doctype.sales_invoice.sales_invoice import SalesInvoice, check_if_return_invoice_linked_with_payment_entry, unlink_inter_company_doc
from erpnext.setup.doctype.company.company import update_company_current_month_sales

class SalesInvoice(SalesInvoice):
	def on_cancel(self):
		check_if_return_invoice_linked_with_payment_entry(self)
		#super(SalesInvoice, self).on_cancel()
		SalesInvoice.check_sales_order_on_hold_or_close(self, "sales_order")
		if self.is_return and not self.update_billed_amount_in_sales_order:
			SalesInvoice.status_updater = []

		SalesInvoice.update_status_updater_args(self)
		SalesInvoice.update_prevdoc_status(self)
		SalesInvoice.update_billing_status_in_dn(self)

		if not self.is_return:
			SalesInvoice.update_billing_status_for_zero_amount_refdoc(self, "Delivery Note")
			SalesInvoice.update_billing_status_for_zero_amount_refdoc(self, "Sales Order")
			SalesInvoice.update_serial_no(self, in_cancel=True)

		# Updating stock ledger should always be called after updating prevdoc status,
		# because updating reserved qty in bin depends upon updated delivered qty in SO
		if self.update_stock == 1:
			SalesInvoice.update_stock_ledger(self)

		SalesInvoice.make_gl_entries_on_cancel(self)

		if self.update_stock == 1:
			SalesInvoice.repost_future_sle_and_gle(self)

		self.db_set("status", "Cancelled")
		self.db_set("repost_required", 0)

		if (
			frappe.db.get_single_value("Selling Settings", "sales_update_frequency") == "Each Transaction"
		):
			update_company_current_month_sales(self.company)
			SalesInvoice.update_project(self)
		if not self.is_return and not self.is_consolidated and self.loyalty_program:
			SalesInvoice.delete_loyalty_point_entry(self)
		elif (
			self.is_return and self.return_against and not self.is_consolidated and self.loyalty_program
		):
			against_si_doc = frappe.get_doc("Sales Invoice", self.return_against)
			against_si_doc.delete_loyalty_point_entry()
			against_si_doc.make_loyalty_point_entry()

		unlink_inter_company_doc(self.doctype, self.name, self.inter_company_invoice_reference)

		SalesInvoice.unlink_sales_invoice_from_timesheets(self)
		self.ignore_linked_doctypes = (
			"GL Entry",
			"Stock Ledger Entry",
			"Repost Item Valuation",
			"Repost Payment Ledger",
			"Repost Payment Ledger Items",
			"Payment Ledger Entry",
		)
		get_items = frappe.db.sql(f""" select name from `tabMaintenance Item` WHERE sales_invoice = '{self.name}' and warranty_status='Enabled' """)
		if get_items:
			for x in get_items:
				frappe.db.set_value("Maintenance Item", x[0], "warranty_status", "")
        


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
                frappe.msgprint("Maintenance Item Created Successfully")
        return "Maintenance Item Created Successfully"
