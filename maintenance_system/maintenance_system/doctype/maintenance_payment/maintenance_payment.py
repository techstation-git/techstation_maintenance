# -*- coding: utf-8 -*-
# Copyright (c) 2020, Tech Station and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class MaintenancePayment(Document):
# Cancel All GL Entry Linked With Given Condition
	def on_cancel(self):
		gl = frappe.get_list('GL Entry', filters={'voucher_no': self.name, 'voucher_type': 'Maintenance Payment'}, fields=['name'])
		for i in gl:
			frappe.db.sql(""" delete from `tabGL Entry` where name= %s """,(i['name']))

		for d in self.references:
			if d.reference_doctype == 'Maintenance Invoice':
				query = """ select IFNULL((select service_net_total from `tabMaintenance Invoice` where name='{0}'),0) - IFNULL(sum(ref.allocated_amount),0), IFNULL(sum(pay.paid_amount), 0) 
				from `tabMaintenance Payment Reference` as ref inner join `tabMaintenance Payment` as pay 
				on ref.parent = pay.name 
				where pay.docstatus!=2 and pay.name!='{1}' and ref.reference_name='{0}' """.format(d.reference_name, self.name)
				get_sums = frappe.db.sql(query)
				
				if get_sums:
					frappe.db.set_value("Maintenance Invoice",d.reference_name,"outstanding_amount",get_sums[0][0])
					frappe.db.set_value("Maintenance Invoice",d.reference_name,"paid_amount",get_sums[0][1])
					if float(get_sums[0][1]) > 0.0 and float(get_sums[0][0]) > 0.0:
						frappe.db.set_value("Maintenance Invoice", d.reference_name, "status", "Partly Paid")
						
						
					if float(get_sums[0][1]) == 0.0 and float(get_sums[0][0]) > 0.0:
						frappe.db.set_value("Maintenance Invoice", d.reference_name, "status", "Unpaid")
						
						
					if float(get_sums[0][0]) > 0.0:
						morder, mproc, type, mdir = frappe.db.get_value("Maintenance Invoice", d.reference_name ,["maintenance_order","processing","processing_type","maintenance_directing"])
						if morder:
							mo = frappe.get_doc("Maintenance Order",morder)
							mo.status = "Unpaid"
							mo.flags.ignore_mandatory=True
							mo.save(ignore_permissions=True)

						if mproc:
							mp = frappe.get_doc(type,mproc)
							mp.status = "Unpaid"
							mp.save(ignore_permissions=True)

						if mdir:
							mo = frappe.get_doc("Maintenance Directing",mdir)
							mo.status = "Unpaid"
							mo.flags.ignore_mandatory=True
							mo.save(ignore_permissions=True)


		
					
	def on_submit(self):
		if self.unallocated_amount > 0:
			self.status = "Balance Available"
			self.save()

		if self.unallocated_amount == 0:
			self.status = "Allocated"
			self.save()

		if not self.references:
			gl_entry = frappe.get_doc({
			"doctype": "GL Entry",
			"posting_date": self.posting_date,
			"voucher_type": self.doctype,
			"voucher_no": self.name,
			"party_type": "Customer",
			"party": self.party,
			"against" : self.paid_to,
			"cost_center": self.cost_center,
			"account": self.paid_from,
			"unallocated": 1,
			"credit": self.unallocated_amount,
			"credit_in_account_currency": self.unallocated_amount,
			"remarks": "Amount {} {} From {}".format(self.paid_amount, self.payment_type, self.party)
			})
			gl_entry.insert(ignore_permissions=True)
			gl_entry.submit()

		if self.references:
			for d in self.references:
				gl_entry = frappe.get_doc({
				"doctype": "GL Entry",
				"posting_date": self.posting_date,
				"against_voucher_type": d.reference_doctype,
				"against_voucher": d.reference_name,
				"voucher_type": self.doctype,
				"voucher_no": self.name,
				"party_type": "Customer",
				"party": self.party,
				"against" : self.paid_to,
				"cost_center": self.cost_center,
				"account": self.paid_from,
				"credit": d.allocated_amount,
				"credit_in_account_currency": d.allocated_amount,
				"remarks": "Amount {} {} From {}, Amount {} Against {} {}".format(self.paid_amount, self.payment_type, self.party,d.allocated_amount,d.reference_doctype,d.reference_name)
				})
				gl_entry.insert(ignore_permissions=True)
				gl_entry.submit()

				if d.reference_doctype == 'Maintenance Invoice':
					query = """ select IFNULL((select service_net_total from `tabMaintenance Invoice` where name='{0}'),0) - IFNULL(sum(ref.allocated_amount),0), IFNULL(sum(pay.paid_amount), 0) 
				from `tabMaintenance Payment Reference` as ref inner join `tabMaintenance Payment` as pay 
				on ref.parent = pay.name 
				where pay.docstatus!=2 and ref.reference_name='{0}' """.format(d.reference_name, self.name)
					get_sums = frappe.db.sql(query)
					if get_sums:
						frappe.db.set_value("Maintenance Invoice",d.reference_name,"outstanding_amount",get_sums[0][0])
						frappe.db.set_value("Maintenance Invoice",d.reference_name,"paid_amount",get_sums[0][1])
						if float(get_sums[0][1]) > 0.0 and float(get_sums[0][0]) > 0.0:
							frappe.db.set_value("Maintenance Invoice", d.reference_name, "status", "Partly Paid")
						if float(get_sums[0][0]) == 0.0:
							frappe.db.set_value("Maintenance Invoice", d.reference_name, "status", "Paid")
							frappe.db.set_value("Maintenance Invoice", d.reference_name, "payment_received", 1)
							morder, mproc, type, mdir = frappe.db.get_value("Maintenance Invoice", d.reference_name ,["maintenance_order","processing","processing_type","maintenance_directing"])
							if morder:
								mo = frappe.get_doc("Maintenance Order",morder)
								mo.status = "Paid"
								mo.flags.ignore_mandatory=True
								mo.save(ignore_permissions=True)
							if mproc:
								mp = frappe.get_doc(type,mproc)
								mp.status = "Paid"
								mp.save(ignore_permissions=True)
								
							if mdir:
								mo = frappe.get_doc("Maintenance Directing",mdir)
								mo.status = "Paid"
								mo.flags.ignore_mandatory=True
								mo.save(ignore_permissions=True)


			if self.unallocated_amount > 0:
				gl_entry = frappe.get_doc({
				"doctype": "GL Entry",
				"posting_date": self.posting_date,
				"voucher_type": self.doctype,
				"voucher_no": self.name,
				"party_type": "Customer",
				"party": self.party,
				"against" : self.paid_to,
				"cost_center": self.cost_center,
				"account": self.paid_from,
				"unallocated": 1,
				"credit": self.unallocated_amount,
				"credit_in_account_currency": self.unallocated_amount,
				"remarks": "Amount {} {} From {}, Amount {} Against {} {}".format(self.paid_amount, self.payment_type,self.party,d.allocated_amount,d.reference_doctype,d.reference_name)
				})
				gl_entry.insert(ignore_permissions=True)
				gl_entry.submit()



		gl = frappe.get_doc({
		"doctype": "GL Entry",
		"posting_date": self.posting_date,
		"voucher_type": self.doctype,
		"voucher_no": self.name,
		"cost_center": self.cost_center,
		"account": self.paid_to,
		"against" : self.party,
		"debit": self.paid_amount,
		"debit_in_account_currency": self.paid_amount,
		"remarks": "Amount {} {} From {}".format(self.paid_amount, self.payment_type, self.party)
		})
		gl.insert(ignore_permissions=True)
		gl.submit()



@frappe.whitelist(allow_guest=True)
def getMINV(party):
	pe = frappe.db.sql("""select name,posting_date,rounded_total,outstanding_amount from `tabMaintenance Invoice` where
                        outstanding_amount > 0 and docstatus = 1 and customer = %s;""",(party),as_list=1)
	return pe if pe else ""

