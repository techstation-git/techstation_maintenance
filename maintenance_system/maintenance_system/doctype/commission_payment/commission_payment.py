# Copyright (c) 2022, Tech Station and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class CommissionPayment(Document):
    def validate(self):
        pass

    def on_update(self):
        full_name=frappe.db.get_value("User",{"name":frappe.session.user},"full_name")
        if self.workflow_state == "Approved":
            frappe.db.set_value(self.doctype,self.name,"approved_by",full_name)
        self.reload()

    def on_submit(self):
        if self.beneficiary and self.status == "Approved":
            if self.table_6:
                for item in self.table_6:
                    if item.maintenance_invoice:
                        # frappe.db.set_value("Maintenance Invoice", item.maintenance_invoice, {
                        #                     "commission_paid": 1})
                        invoice = frappe.get_doc(
                            "Maintenance Invoice", item.maintenance_invoice)
                        if invoice.get("table_127"):
                            for data in invoice.get("table_127"):
                                if data.get("team") == self.beneficiary:
                                    frappe.db.set_value("Maintenance Team Table Invoice", data.get(
                                        "name"), {"commission_paid": 1})


            # Calculate GL Entry
            settings=frappe.get_doc("Maintenance System Settings")
            cost_center = frappe.db.get_value("Company", self.company ,["cost_center"])
            if settings.payment_commission_from_account and settings.payment_commission_to_account:
                gl_entry = frappe.get_doc({
				    "doctype": "GL Entry",
				    "posting_date": self.posting_date,
				    "party": self.beneficiary,
				    "voucher_type": self.doctype,
				    "party_type": "Maintenance Team",
				    "voucher_no": self.name,
				    "cost_center": cost_center,
				    "account": settings.payment_commission_from_account,
				    "against": settings.payment_commission_to_account,
				    "debit": self.total_commission,
				    "debit_in_account_currency": self.total_commission
			    })
                gl_entry.insert(ignore_permissions=True)
                gl_entry.submit()
            else:
                frappe.throw("Please Set Commission From Account To To Account in Maintenance System Settiings")
            frappe.msgprint("Successfully Approved")

    def on_cancel(self):
        if self.beneficiary and self.status == "Rejected":
            if self.table_6:
                for item in self.table_6:
                    if item.maintenance_invoice:
                        # frappe.db.set_value("Maintenance Invoice", item.maintenance_invoice, {
                        #                     "commission_paid": 0})
                        invoice = frappe.get_doc(
                            "Maintenance Invoice", item.maintenance_invoice)
                        if invoice.get("table_127"):
                            for data in invoice.get("table_127"):
                                if data.get("team") == self.beneficiary:
                                    frappe.db.set_value("Maintenance Team Table Invoice", data.get(
                                        "name"), {"commission_paid": 0})

			#Calculate Commission On Cancel
            get_gl_entry=frappe.get_value("GL Entry",{"party":self.beneficiary,"party_type": "Maintenance Team","voucher_no": self.name},["name"])
            if get_gl_entry:
                frappe.db.delete("GL Entry", {"name": get_gl_entry})
            settings=frappe.get_doc("Maintenance System Settings")
            full_name=frappe.db.get_value("User",{"name":frappe.session.user},"full_name")
            if self.workflow_state == "Rejected":
                frappe.db.set_value(self.doctype,self.name,"rejected_by",full_name)
            cost_center = frappe.db.get_value("Company", self.company ,["cost_center"])
            frappe.msgprint("Successfully Canceled")
            self.reload()


@frappe.whitelist()
def get_invoices(team,commission):
	chec_commi=""
	if commission == "Net Total":
		chec_commi = "mi.service_net_total"
	else:
		chec_commi="mi.grand_total"
	if team:
		get_paid_invoice = frappe.db.sql(
            f"""select tti.team as team,mi.name as name,mi.posting_date as posting_date,mi.payment_method as payment_method, {chec_commi} as paid_amount, tti.commission_paid as commission_paid from `tabMaintenance Invoice` mi left join `tabMaintenance Team Table Invoice` tti on mi.name = tti.parent where mi.status='Paid' and tti.team='{team}' and tti.commission_paid=0""", as_dict=1)
		if len(get_paid_invoice) > 0:
			paid_invoice=[]
			get_invoices_name=[]
			for names in get_paid_invoice:
				if names.name not in get_invoices_name:
					get_invoices_name.append(names.name)
					paid_invoice.append(names)
			return paid_invoice
		else:
			frappe.msgprint(
                f"Paid Maintenance Invoice not Found for {team} Maintenance Team")
        # pass
