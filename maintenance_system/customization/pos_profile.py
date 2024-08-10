import frappe

def create_delete_pos_profile(self,method=None):
    if self.applicable_for_users:
        if not self.disabled:
            for row in self.applicable_for_users:
                pos_profile=frappe.db.get_value("Maintenance POS Profile",{"user":row.user,"pos_profile":self.name},"name")
                if not pos_profile:
                    user_per = frappe.new_doc('Maintenance POS Profile')
                    user_per.user=row.user
                    user_per.enable=1
                    user_per.pos_profile= self.name
                    user_per.default = 1
                    user_per.insert()
        else:
            for row in self.applicable_for_users:
                pos_profile=frappe.db.get_value("Maintenance POS Profile",{"user":row.user,"for_value":self.warehouse},"name")
                if pos_profile:
                    invoice = frappe.get_doc('Maintenance POS Profile', pos_profile)
                    invoice.delete()