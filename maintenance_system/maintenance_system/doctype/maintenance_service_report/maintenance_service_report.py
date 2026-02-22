import frappe
from frappe.model.document import Document
from frappe import _

class MaintenanceServiceReport(Document):
	def validate(self):
		if not self.customer_signature:
			frappe.throw(_("Customer Signature is required before submitting the service report."))
		
		# Ensure technician is linked to an employee
		if not self.technician:
			employee = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")
			if employee:
				self.technician = employee

	def on_submit(self):
		# Update Maintenance Order or notify users if needed
		pass

	def on_cancel(self):
		pass
