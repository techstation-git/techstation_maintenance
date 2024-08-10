# -*- coding: utf-8 -*-
# Copyright (c) 2020, Tech Station and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class MaintenanceTeam(Document):
	
	def on_update(self):

		if self.enable:
			count_enable=frappe.db.sql(f"select name from `tabMaintenance Team` where user='{self.user}' and enable = 1",as_list=1)
			if len(count_enable) > 1:
				frappe.throw(f"You Can Only enable 1 Maintenace Team for user {self.user}")
			self.reload()
			frappe.clear_cache()
	def on_update_after_submit(self):
		if self.warehouse:
			if self.enable:
				warehouse_doc=frappe.db.get_value("User Permission",{"user":self.user,"for_value":self.warehouse},"name")
				if not warehouse_doc:
					user_per = frappe.new_doc('User Permission')
					user_per.user=self.user
					user_per.allow="Warehouse"
					user_per.for_value= self.warehouse
					user_per.apply_to_all_doctypes = 1
					user_per.insert()
			else:
				warehouse_doc=frappe.db.get_value("User Permission",{"user":self.user,"for_value":self.warehouse},"name")
				if warehouse_doc:
					invoice = frappe.get_doc('User Permission', warehouse_doc)
					invoice.delete()
		if self.enable:
			count_enable=frappe.db.sql(f"select name from `tabMaintenance Team` where user='{self.user}' and enable = 1",as_list=1)
			if len(count_enable) > 1:
				frappe.throw(f"You Can Only enable 1 Maintenace Team for {self.user}")
			self.reload()
			frappe.clear_cache()
	def on_submit(self):
		if self.enable and self.warehouse:
			user_per = frappe.new_doc('User Permission')
			user_per.user=self.user
			user_per.allow="Warehouse"
			user_per.for_value= self.warehouse
			user_per.apply_to_all_doctypes = 1
			user_per.insert()
	def on_cancel(self):
		if self.warehouse:
			warehouse_doc=frappe.db.get_value("User Permission",{"user":self.user,"for_value":self.warehouse},"name")
			if warehouse_doc:
				invoice = frappe.get_doc('User Permission', warehouse_doc)
				invoice.delete()
