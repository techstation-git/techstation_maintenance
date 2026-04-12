import frappe

@frappe.whitelist()
def on_update_mobile(self,method=None):
    mobile = getattr(self, "mobile", None)
    if mobile:
        self.mobile_no = mobile