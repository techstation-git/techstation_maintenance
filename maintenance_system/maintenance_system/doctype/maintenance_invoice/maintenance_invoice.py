# -*- coding: utf-8 -*-
# Copyright (c) 2020, Tech Station and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.mapper import get_mapped_doc
from frappe.utils.csvutils import getlink
from frappe import msgprint, _
from frappe.model.document import Document
from datetime import datetime


class MaintenanceInvoice(Document):
	def validate(self):
		get_maintenance_profile(self)
		if not self.current_stage:
			self.current_stage = 'Maintenance Invoice'
		if not self.confirmed_by:
			self.confirmed_by = frappe.session.user
		if self.outstanding_amount == 0:
			self.status = "Paid"

		if self.outstanding_amount > 0.0:
			self.status = "Unpaid"
		self.db_set("status", self.status, update_modified=True)

		self.calculate_discount()
		
	def calculate_discount(self):
		self.service_total = 0.0
		if self.service:
			for val in self.service:
				self.service_total += val.price
		discount_on_items = 0.0
		discount_on_services = 0.0

		posting_date = datetime.strptime(str(self.posting_date), "%Y-%m-%d")
		for item in self.warranty_bearing_rate:
			warranty_start_date = datetime.strptime(str(item.warranty_start_date), "%Y-%m-%d")
			warranty_end_date = datetime.strptime(str(item.warranty_end_date), "%Y-%m-%d")
			if posting_date >= warranty_start_date and posting_date <= warranty_end_date:
				discount_on_items += item.repairing_tolerance_item
				discount_on_services += item.repairing_tolerance_services
				break
		
		self.company_bearing_ratio_for_item = discount_on_items		
		self.company_bearing_ratio_for_service = discount_on_services
		discount_on_items += self.additional_discount_on_items
		discount_on_services += self.additional_discount_for_services
		if float(discount_on_items) > 100.0:
			frappe.throw("Item Percentage must be less then 100%")
		if float(discount_on_services) > 100.0:
			frappe.throw("Services Percentage must be less then 100%")
			
		self.grand_total = self.service_total + self.total_amount
		self.warranty_bearing_percentage = discount_on_items + discount_on_services
		if self.company_bearing_ratio_for_item > 0.0 or self.company_bearing_ratio_for_service > 0.0:
			self.warranty_apply = 1
		
		self.warranty_bearing_discount_on_item = (self.total_amount * discount_on_items)/100.0
		self.warranty_bearing_discount_on_service = (self.service_total * discount_on_services)/100.0
		self.warranty_total = float(self.warranty_bearing_discount_on_item) + float(self.warranty_bearing_discount_on_service)
		self.service_net_total = self.grand_total - self.warranty_bearing_discount_on_item - self.warranty_bearing_discount_on_service
		#self.service_net_total = self.grand_total - self.warranty_total
		self.outstanding_amount = self.service_net_total - self.paid_amount


	def on_submit(self):
		get_maintenance_profile(self)
		if self.receive_maintenance_items:
			frappe.db.set_value("Receive Maintenance Item",self.receive_maintenance_items,"completed_maintenance",1)
		mf = frappe.get_doc({
		"doctype": "Maintenance Feedback",
		"invoice_date": self.posting_date,
		"customer": self.customer,
		"invoice_number": self.name
		})
		mf.insert(ignore_permissions=True)
		mf.save(ignore_permissions=True)
		if self.warranty_template_repair:
			from frappe.utils import today
			from frappe.utils import add_to_date
			from datetime import datetime
			warranty_template_period=frappe.db.get_value("Warranty Template",self.warranty_template_repair,"warranty_period")
			self.warranty_start_date_repair=today()
			self.warranty_expiry_date_repair=add_to_date(datetime.now(), days=warranty_template_period, as_string=True)


		if self.get_advance_payment and self.outstanding_amount == 0:
			self.status = "Paid"
			self.save()
		

		if self.maintenance_order and self.outstanding_amount > 0.0:
			mo = frappe.get_doc("Maintenance Order",self.maintenance_order)
			mo.status = "Unpaid"
			mo.flags.ignore_mandatory=True
			mo.save(ignore_permissions=True)

		if self.processing and self.outstanding_amount > 0.0:
			mp = frappe.get_doc(self.processing_type,self.processing)
			mp.status = "Unpaid"
			mp.flags.ignore_mandatory=True
			mp.save(ignore_permissions=True)

		if self.maintenance_order and self.outstanding_amount == 0.0:
			mo = frappe.get_doc("Maintenance Order",self.maintenance_order)
			mo.status = "Paid"
			mo.flags.ignore_mandatory=True
			mo.save(ignore_permissions=True)

		if self.processing and self.outstanding_amount == 0.0:
			mp = frappe.get_doc(self.processing_type,self.processing)
			mp.maintenance_invoice = self.name
			mp.status = "Paid"
			mp.flags.ignore_mandatory=True
			mp.save(ignore_permissions=True)

		debit, cost_center, income, round_off_account = frappe.db.get_value("Company", self.company ,["default_receivable_account", "cost_center","default_income_account","round_off_account"])


		if self.warranty_apply ==1:
			warranty_expense_account=frappe.get_doc("Maintenance System Settings")
			if 	warranty_expense_account.from_account and warranty_expense_account.to_account:
						gl_entry = frappe.get_doc({
						"doctype": "GL Entry",
						"posting_date": self.posting_date,
						"party": self.customer,
						"voucher_type": self.doctype,
						"party_type": "Customer",
						"voucher_no": self.name,
						"cost_center": cost_center,
						"account": warranty_expense_account.from_account,
						"against" : warranty_expense_account.to_account,
						"debit": self.warranty_total,
						"debit_in_account_currency": self.warranty_total
						})
						gl_entry.insert(ignore_permissions=True)
						gl_entry.submit()
		# Debit Account Debit
		if self.grand_total > 0:
			gl_entry = frappe.get_doc({
			"doctype": "GL Entry",
			"posting_date": self.posting_date,
			"party": self.customer,
			"voucher_type": self.doctype,
			"party_type": "Customer",
			"voucher_no": self.name,
			"cost_center": cost_center,
			"account": debit,
			"against" : income,
			"debit": self.grand_total,
			"debit_in_account_currency": self.grand_total
			})
			gl_entry.insert(ignore_permissions=True)
			gl_entry.submit()

	# # Income Account Credit
		if self.grand_total > 0:
			gl_entry = frappe.get_doc({
			"doctype": "GL Entry",
			"posting_date": self.posting_date,
			"party": self.customer,
			"voucher_type": self.doctype,
			"party_type": "Customer",
			"voucher_no": self.name,
			"cost_center": cost_center,
			"account": income,
			"credit": self.grand_total,
			"credit_in_account_currency": self.grand_total
			})
			gl_entry.insert(ignore_permissions=True)
			gl_entry.submit()

	# Taxes

		if self.sales_taxes_and_charges_template:
			for d in self.tax:
				if d.tax_amount > 0:
					gl_entry = frappe.get_doc({
					"doctype": "GL Entry",
					"posting_date": self.posting_date,
					"voucher_type": self.doctype,
					"voucher_no": self.name,
					"cost_center": cost_center,
					"account": d.account_head,
					"credit": d.tax_amount,
					"credit_in_account_currency": d.tax_amount
					})
					gl_entry.insert(ignore_permissions=True)
					gl_entry.submit()


		if self.maintenance_advance_payment:
			for i in self.maintenance_advance_payment:
				mpe = frappe.get_doc("Maintenance Payment",i.payment_entry)
				mpe.unallocated_amount = i.pending
				mpe.total_allocated_amount += i.allocate_amount
				ct = mpe.append("references",{})
				ct.reference_doctype = self.doctype
				ct.reference_name = self.name
				ct.due_date = self.posting_date
				ct.total_amount = self.rounded_total
				ct.outstanding_amount = self.outstanding_amount
				ct.allocated_amount = i.allocate_amount
				if mpe.unallocated_amount == 0:
					mpe.status = "Allocated"
					mpe.save()
				else:
					mpe.save()

				mi = frappe.get_list('GL Entry', filters={"unallocated": 1}, fields=['name'])
				for a in mi:
					gl_entry = frappe.get_doc("GL Entry",a)
					gl_entry.cancel()
					gl_entry.delete()
				gl_entry = frappe.get_doc({
				"doctype": "GL Entry",
				"posting_date": self.posting_date,
				"against_voucher_type": self.doctype,
				"against_voucher": self.name,
				"voucher_type": "Maintenance Payment",
				"voucher_no": i.payment_entry,
				"party_type": "Customer",
				"party": self.customer,
				"against" : i.paid_to,
				"cost_center": i.cost_center,
				"account": i.paid_from,
				"credit": i.allocate_amount,
				"credit_in_account_currency": i.allocate_amount,
				"remarks": "Amount {} Received From Customer {}, Amount {} Against {} {}".format(i.total_amount,self.customer,i.allocate_amount,self.doctype,self.name)
				})
				gl_entry.insert(ignore_permissions=True)
				gl_entry.submit()

				if i.pending > 0:
					gl_entry = frappe.get_doc({
					"doctype": "GL Entry",
					"posting_date": self.posting_date,
					"voucher_type": "Maintenance Payment",
					"voucher_no": i.payment_entry,
					"party_type": "Customer",
					"party": self.customer,
					"against" : i.paid_to,
					"cost_center": i.cost_center,
					"account": i.paid_from,
					"unallocated": 1,
					"credit": i.pending,
					"credit_in_account_currency": i.pending,
					"remarks": "Amount {} Received From Customer {}, Amount {} Against {} {}".format(i.total_amount,self.customer,i.allocate_amount,self.doctype,self.name)
					})
					gl_entry.insert(ignore_permissions=True)
					gl_entry.submit()

		if self.processing_type == "External Processing":
			paid_to = ""
			# if self.payment_method == "Cash":
			# 	paid_to = frappe.db.get_single_value('Maintenance System Settings', 'cash_account')

			# if self.payment_method == "Visa":
			# 	paid_to = frappe.db.get_single_value('Maintenance System Settings', 'visa_account')
			mode_list=[]
			frappe.log_error("Mode of payment",self.payment_method)
			paid_to_settings=frappe.get_doc('Maintenance System Settings')
			if paid_to_settings.payment_methods:
				for acc in paid_to_settings.payment_methods:
					mode_list.append(acc.payment_method_name)
					if acc.payment_method_name == self.payment_method:
						paid_to=acc.account

			if self.payment_method not in mode_list:
				frappe.throw(f"Please Add {self.payment_method} Mode of Payment Account in Maintenance System Settings")

			paid_from = frappe.db.get_single_value('Maintenance System Settings', 'debtors_account')
			cost_center = frappe.db.get_single_value('Maintenance System Settings', 'cost_center')

			pe = frappe.get_doc({
			"doctype": "Maintenance Payment",
			"payment_type": "Receive",
			"company": self.company,
			"posting_date": self.posting_date,
			"mode_of_payment": self.payment_method,
			"cost_center": cost_center,
			"party": self.customer,
			"paid_from": paid_from,
			"paid_to": paid_to,
			"paid_amount": self.grand_total,
			"total_allocated_amount" : self.grand_total,
			"unallocated_amount": 0.0,
			"references": [{
				"reference_doctype": "Maintenance Invoice",
				"reference_name": self.name,
				"due_date": self.posting_date,
				"total_amount": self.grand_total,
				"outstanding_amount": self.outstanding_amount,
				"allocated_amount": self.grand_total,
				"pending" : 0.0
			}]
			})
			pe.insert(ignore_permissions=True)
			pe.save(ignore_permissions=True)
			pe.submit()
			frappe.msgprint("Maintenance Payment Created")


		team_list=[]
		if self.processing_type and self.processing:
			or_doc=frappe.get_doc(self.processing_type,self.processing)
			if self.processing_type == "Internal Processing":
				if or_doc.table_115:
					for item in or_doc.table_115:
						dict3={}
						dict3["stages"]=item.stages
						dict3["team"]=item.team
						team_list.append(dict3)
			if self.processing_type == "External Processing":
				if or_doc.table_118:
					for item in or_doc.table_118:
						dict4={}
						dict4["stages"]=item.stages
						dict4["team"]=item.team
						team_list.append(dict4)

		if self.commission_benificiary:
			data_doc = {}
			data_doc["stages"]=self.doctype
			data_doc["team"]=self.commission_benificiary
			team_list.append(data_doc)
			# frappe.throw("Error")
		else:
			data_doc = {}
			data_doc["stages"]=self.doctype
			data_doc["team"]= self.maintenance_team
			team_list.append(data_doc)
		if team_list:
			for data in team_list:
				data_doc1=frappe.new_doc("Maintenance Team Table Invoice")
				data_doc1.parent=self.name
				data_doc1.parenttype=self.doctype
				data_doc1.parentfield="table_127"
				data_doc1.stages=data.get("stages")
				data_doc1.team=data.get("team")
				data_doc1.insert()
			frappe.clear_cache()
			self.reload()

# Cancel Entry

	def on_cancel(self):
		gl = frappe.get_list('GL Entry', filters={'voucher_no': self.name}, fields=['name'])
		for i in gl:
			gl_entry = frappe.get_doc("GL Entry",i)
			gl_entry.cancel()
			gl_entry.delete()

		if self.maintenance_order:
			mo = frappe.get_doc("Maintenance Order",self.maintenance_order)
			mo.status = "Under Maintenance"
			mo.save(ignore_permissions=True)

		if self.processing:
			mp = frappe.get_doc(self.processing_type,self.processing)
			mp.status = "Start"
			mp.maintenance_invoice = "undefined"
			mp.save(ignore_permissions=True)

		if self.maintenance_advance_payment:
			for d in self.maintenance_advance_payment:
				mi = frappe.get_list('GL Entry', filters={'against_voucher': self.name,"voucher_no":d.payment_entry}, fields=['name'])
				if mi:
					for i in mi:
						gl_entry = frappe.get_doc("GL Entry",i)
						gl_entry.cancel()
						gl_entry.delete()

				mi = frappe.get_list('GL Entry', filters={"unallocated": 1}, fields=['name'])
				for a in mi:
					gl_entry = frappe.get_doc("GL Entry",a)
					gl_entry.cancel()
					gl_entry.delete()

				gl_entry = frappe.get_doc({
				"doctype": "GL Entry",
				"posting_date": self.posting_date,
				"voucher_type": "Maintenance Payment",
				"voucher_no": d.payment_entry,
				"party_type": "Customer",
				"party": self.customer,
				"against" : d.paid_to,
				"cost_center": d.cost_center,
				"account": d.paid_from,
				"unallocated": 1,
				"credit": d.pending + d.allocate_amount,
				"credit_in_account_currency": d.pending + d.allocate_amount,
				"remarks": "Amount {} Received From {}".format(d.total_amount, self.customer)
				})
				gl_entry.insert(ignore_permissions=True)
				gl_entry.submit()


				mpe = frappe.get_doc("Maintenance Payment",d.payment_entry)
				mpe.unallocated_amount += d.allocate_amount
				mpe.total_allocated_amount -= d.allocate_amount
				if mpe.unallocated_amount != 0:
					mpe.status = "Balance Available"
				for j in mpe.references:
					if j.reference_name == self.name:
						mpe.remove(j)
						mpe.save(ignore_permissions=True)
					else:
						mpe.save(ignore_permissions=True)





@frappe.whitelist()
def make_payment_entry(doc,mode,doctype,docname,posting_date):
	mi = frappe.get_doc('Maintenance Order', doc)
	paid_to=""
	
	mode_list=[]
	paid_to_settings=frappe.get_doc('Maintenance System Settings')
	if paid_to_settings.payment_methods:
		for acc in paid_to_settings.payment_methods:
			mode_list.append(acc.payment_method_name)
			if acc.payment_method_name == mode:
				paid_to=acc.account
	if mode not in mode_list:
		frappe.throw(f"Please Add {mode} Mode of Payment Account in Maintenance System Settings")
	# if mode == "Visa":
	# 	paid_to_settings = frappe.db.get_single_value('Maintenance System Settings', 'visa_account')

	paid_from = frappe.db.get_single_value('Maintenance System Settings', 'debtors_account')
	cost_center = frappe.db.get_single_value('Maintenance System Settings', 'cost_center')

	pe = frappe.get_doc({
	"doctype": "Maintenance Payment",
	"payment_type": "Receive",
	"company": mi.company,
	"posting_date":posting_date,
	"mode_of_payment": mode,
	"cost_center": cost_center,
	"party": mi.customer,
	"paid_from": paid_from,
	"paid_to": paid_to,
	"paid_amount": mi.total_amount,
	"total_allocated_amount" : mi.total_amount,
	"unallocated_amount": 0.0,
	"references": [{
		"reference_doctype": "Maintenance Order",
		"reference_name": mi.name,
		"due_date": posting_date,
		"total_amount": mi.total_amount,
		"outstanding_amount": mi.total_amount,
		"allocated_amount": mi.total_amount,
		"pending" : 0.0
		}]
	})
	pe.insert(ignore_permissions=True)
	pe.save(ignore_permissions=True)
	pe.submit()
	frappe.db.set_value(doctype,docname,"maintenance_payment",pe.name)
	frappe.db.set_value(doctype,docname,"status","Payment Received")
	frappe.db.set_value(doctype,docname,"payment_received",1)
	if mi.total_amount < pe.paid_amount:
		frappe.db.set_value(doctype,docname,"advance_paid",pe.paid_amount-mi.total_amount)
	elif mi.total_amount > pe.paid_amount:
		frappe.db.set_value(doctype,docname,"outstanding_amount",mi.total_amount-pe.paid_amount)
	else:
		frappe.db.set_value(doctype,docname,"outstanding_amount",0)
	frappe.clear_cache()
	mi.reload()
	frappe.msgprint(_("Maintenance Payment is Created: {0}").format(getlink('Maintenance Payment', pe.name)))


@frappe.whitelist()
def make_payment_entry_invoice(doc, mode, allocated_amount, outstanding):
	mi = frappe.get_doc('Maintenance Invoice', doc)
	paid_to=""
	mode_list=[]
	paid_to_settings=frappe.get_doc('Maintenance System Settings')
	if paid_to_settings.payment_methods:
		for acc in paid_to_settings.payment_methods:
			mode_list.append(acc.payment_method_name)
			if acc.payment_method_name == mode:
				paid_to=acc.account

	if mode not in mode_list:
		frappe.throw(f"Please Add {mode} Mode of Payment Account in Maintenance System Settings")

	paid_from = frappe.db.get_single_value('Maintenance System Settings', 'debtors_account')
	cost_center = frappe.db.get_single_value('Maintenance System Settings', 'cost_center')

	pe = frappe.get_doc({
	"doctype": "Maintenance Payment",
	"payment_type": "Receive",
	"company": mi.company,
	"posting_date":mi.posting_date,
	"mode_of_payment": mode,
	"cost_center": cost_center,
	"party": mi.customer,
	"paid_from": paid_from,
	"paid_to": paid_to,
	"paid_amount": allocated_amount,
	"total_allocated_amount" : allocated_amount,
	"unallocated_amount": 0.0,
	"references": [{
		"reference_doctype": "Maintenance Invoice",
		"reference_name": mi.name,
		"due_date":mi.posting_date,
		"total_amount": mi.grand_total,
		"outstanding_amount": float(outstanding),
		"allocated_amount": allocated_amount,
		"pending" : 0.0
		}]
	})
	pe.insert(ignore_permissions=True)
	pe.save(ignore_permissions=True)
	pe.submit()
	if pe.name:
		frappe.clear_cache()
		mi.reload()
		frappe.msgprint(_("Maintenance Payment is Created: {0}").format(getlink('Maintenance Payment', pe.name)))

@frappe.whitelist()
def get_maintenance_profile(self):
    if self.maintenance_team:
        get_profile=frappe.db.sql(f"""select po.name from `tabPOS Profile` po left join `tabPOS Profile User` pu on po.name=pu.parent where po.disabled=0 and pu.user='{frappe.session.user}' and pu.default=1""",as_dict=1)
        if len(get_profile) > 0:
            self.pos_profile=get_profile[0]["name"]
        else:
            self.pos_profile=""
            # self.save()
        # self.reload()
        return get_profile
        
@frappe.whitelist()
def fetch_template(source_name, target_doc=None):
	target_doc = get_mapped_doc("Maintenance Item", source_name, {
		"Maintenance Item": {
			"doctype": "Maintenance Invoice",
		},
		"Maintenance Item Warranty Bearing": {
			"doctype": "Maintenance Item Warranty Bearing",
		}
	}, target_doc)

	return target_doc



    
