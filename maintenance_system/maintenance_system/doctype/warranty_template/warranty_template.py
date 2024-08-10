# -*- coding: utf-8 -*-
# Copyright (c) 2020, Tech Station and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class WarrantyTemplate(Document):
	
	def validate(self):
		list_data=[]
		if self.warranty_bearing_rate:
			for rate in self.warranty_bearing_rate:
				if rate.repairing_tolerance:
					if float(rate.repairing_tolerance) > 100:
						list_data.append(rate.idx)
		if len(list_data) > 0:
			frappe.throw(f"Repairing Tolerance should not be greater than 100 at row {str(list_data)[1:-1]}")
		
		if self.warranty_period:
			if self.warranty_period_type != "Days":
				if len(self.warranty_bearing_rate) > self.warranty_period:
					frappe.throw("Warranty Bearing Rate Con Not greater than Warranty Period ")
				elif len(self.warranty_bearing_rate) < self.warranty_period:
					frappe.throw("Warranty Bearing Rate Con Not Less than Warranty Period ")
				else:
					frappe.msgprint("Warranty Template Successfully Created")

