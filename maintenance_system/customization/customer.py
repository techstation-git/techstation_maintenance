import frappe

@frappe.whitelist()
def on_update_mobile(self,method=None):
    if self.mobile:
        self.mobile_no=self.mobile