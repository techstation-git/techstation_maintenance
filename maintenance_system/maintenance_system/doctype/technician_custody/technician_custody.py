# -*- coding: utf-8 -*-
# Copyright (c) 2026, Tech Station and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import flt, today, getdate


class TechnicianCustody(Document):
	def validate(self):
		"""Validate custody before saving"""
		self.calculate_totals()
		self.update_status()
		self.validate_return_quantities()
	
	def on_submit(self):
		"""Create stock entry when custody is issued"""
		if not self.stock_entry_issue:
			self.create_stock_entry_issue()
	
	def on_cancel(self):
		"""Cancel related stock entries"""
		if self.stock_entry_issue:
			self.cancel_stock_entry(self.stock_entry_issue)
		if self.stock_entry_return:
			self.cancel_stock_entry(self.stock_entry_return)
	
	def calculate_totals(self):
		"""Calculate total values"""
		total_issue = 0
		total_return = 0
		
		for item in self.items:
			item.issue_value = flt(item.qty_issued) * flt(item.valuation_rate)
			item.return_value = flt(item.qty_returned) * flt(item.valuation_rate)
			total_issue += item.issue_value
			total_return += item.return_value
		
		self.total_issue_value = total_issue
		self.total_return_value = total_return
		self.variance_value = total_issue - total_return
	
	def update_status(self):
		"""Update custody status based on return quantities"""
		if not self.items:
			return
		
		total_issued = sum(flt(item.qty_issued) for item in self.items)
		total_returned = sum(flt(item.qty_returned) for item in self.items)
		
		if total_returned == 0:
			self.custody_status = "Issued"
		elif total_returned >= total_issued:
			self.custody_status = "Fully Returned"
			if not self.actual_return_date:
				self.actual_return_date = today()
		else:
			self.custody_status = "Partially Returned"
		
		# Check if overdue
		if self.expected_return_date and self.custody_status != "Fully Returned":
			if getdate(self.expected_return_date) < getdate(today()):
				self.custody_status = "Overdue"
	
	def validate_return_quantities(self):
		"""Ensure returned quantity doesn't exceed issued quantity"""
		for item in self.items:
			if flt(item.qty_returned) > flt(item.qty_issued):
				frappe.throw(
					f"Row {item.idx}: Returned quantity ({item.qty_returned}) cannot exceed issued quantity ({item.qty_issued}) for {item.item_code}"
				)
	
	def create_stock_entry_issue(self):
		"""Create stock entry for issuing custody items"""
		if not self.items:
			frappe.throw("Cannot create stock entry without items")
		
		stock_entry = frappe.new_doc("Stock Entry")
		stock_entry.stock_entry_type = "Material Issue"
		stock_entry.purpose = "Material Issue"
		stock_entry.company = frappe.defaults.get_user_default("Company")
		
		# Reference this custody record
		stock_entry.add_comment("Comment", f"Custody issued: {self.name} to {self.maintenance_team}")
		
		for item in self.items:
			if flt(item.qty_issued) > 0:
				stock_entry.append("items", {
					"item_code": item.item_code,
					"qty": item.qty_issued,
					"s_warehouse": frappe.db.get_single_value("Stock Settings", "default_warehouse"),
					"t_warehouse": self.get_custody_warehouse(),
					"basic_rate": item.valuation_rate,
					"allow_zero_valuation_rate": 1
				})
		
		stock_entry.insert()
		stock_entry.submit()
		
		self.db_set("stock_entry_issue", stock_entry.name)
		frappe.msgprint(f"Stock Entry {stock_entry.name} created for custody issue")
	
	def get_custody_warehouse(self):
		"""Get or create custody warehouse for this technician"""
		company_abbr = frappe.db.get_value("Company", frappe.defaults.get_user_default("Company"), "abbr")
		warehouse_name = f"Custody - {self.maintenance_team} - {company_abbr}"
		
		if not frappe.db.exists("Warehouse", warehouse_name):
			# Create warehouse if it doesn't exist
			warehouse = frappe.get_doc({
				"doctype": "Warehouse",
				"warehouse_name": f"Custody - {self.maintenance_team}",
				"company": frappe.defaults.get_user_default("Company"),
				"is_group": 0
			})
			warehouse.insert(ignore_permissions=True)
		
		return warehouse_name
	
	def cancel_stock_entry(self, stock_entry_name):
		"""Cancel a stock entry"""
		stock_entry = frappe.get_doc("Stock Entry", stock_entry_name)
		if stock_entry.docstatus == 1:
			stock_entry.cancel()
