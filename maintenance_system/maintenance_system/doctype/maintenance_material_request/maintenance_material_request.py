from frappe.model.document import Document

class MaintenanceMaterialRequest(Document):
    def before_insert(self):
        import frappe
        if not self.requested_by:
            self.requested_by = frappe.session.user
        self.status = "Draft"

    def on_update(self):
        pass
