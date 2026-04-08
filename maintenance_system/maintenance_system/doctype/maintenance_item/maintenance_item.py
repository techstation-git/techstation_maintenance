# -*- coding: utf-8 -*-
# Copyright (c) 2020, Tech Station and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import msgprint
from frappe.model.mapper import get_mapped_doc
from datetime import date
from frappe.model.document import Document
from frappe.model.naming import make_autoname

class MaintenanceItem(Document):
	def validate(self):
		get_all_tolerence(self)
		on_update_data(self)
		
	def before_insert(self):
		if self.sales_invoice and self.item:
			self.check_duplicate_invoice()
			
	def check_duplicate_invoice(self):
		check_already = frappe.db.sql(""" select name from `tabMaintenance Item` where docstatus!=2 and 
			sales_invoice='{0}' and item='{1}' """.format(str(self.sales_invoice), self.item))
		if check_already:
			frappe.throw("Maintenance Item Already Created against Invoice No. <b>{0}</b> ".format(str(self.sales_invoice)))
				
	# def autoname(self):
	# 	self.create_barcode()
	
	def on_update(self):
		on_update_data(self)
		
	def on_cancel(self):
		if self.sales_invoice:
			frappe.db.set_value("Sales Invoice", str(self.sales_invoice), "warranty_created", 0)
	def create_barcode(self):
		if not self.barcode:
			color=""
			model=""
			item=""
			if self.item:
				item=self.item_name
			else:
				if self.item_colors:
					color=self.item_colors
				if self.item_models:
					model=self.item_models
			if self.create_barcode_automatically:
				maintenance_setting=frappe.get_doc("Maintenance System Settings")
				if maintenance_setting.get("generate_barcode_on_barcode_type"):
					if maintenance_setting.get("item_barcode_type"):
						if maintenance_setting.get("item_barcode_type") == "CODE128":
							barcodes = get_random_string(maintenance_setting.get("length"))
							self.barcode=barcodes
							if item:
								self.name=item+"-"+barcodes
							else:
								self.name= model+"-"+color+"-"+barcodes
						elif maintenance_setting.get("item_barcode_type") == "EAN-13":
							barcodes = get_random_number(12)
							self.barcode=barcodes
							if item:
								self.name=item+"-"+barcodes
							else:
								self.name=model+"-"+color+"-"+barcodes
						elif maintenance_setting.get("item_barcode_type") == "UPC-A":
							barcodes = get_random_number(11)
							self.barcode=barcodes
							if item:
								self.name=item+"-"+barcodes
							else:
								self.name=model+"-"+color+"-"+barcodes
					else:
						frappe.throw("Please Slect a Barcode Type for Genearete Barcode Automatically")
				else:
					if maintenance_setting.get("maintenance_item_barcode_series"):
						barcodes=make_autoname(maintenance_setting.get("maintenance_item_barcode_series"))
						self.barcode=barcodes
						if item:
								self.name=item+"-"+barcodes
						else:
							self.name=model+"-"+color+"-"+barcodes
					else:
						frappe.throw("Please Set a Barcode Series For Generate Barcode Automatically")
				frappe.msgprint("Barcode Generated Successfully")



import random
import string

def on_update_data(self):
	if self.item_status:
		data=""
		for item in self.item_status:
			data=data+item.status + " "
		self.maintenance_item_status=data

def on_update_data_self(self,method=None):
	if self.item_status:
		data=""
		for item in self.item_status:
			data=data+item.status + " "
		frappe.db.set_value(self.doctype,self.name,"maintenance_item_status",data)
		frappe.clear_cache()
		self.reload()

def get_random_string(length):
	# choose from all lowercase letter
	letters = string.ascii_uppercase
	# call random.choices() string module to find the string in Uppercase + numeric data.
	result_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k = length))    
	return result_str

def get_random_number(length):
	# choose from all lowercase letter
	letters = string.ascii_uppercase
	# call random.choices() string module to find the string in Uppercase + numeric data.
	result_str = ''.join(random.choices(string.digits, k = length))    
	return result_str

@frappe.whitelist()
def make_receive_maintenance_items(source_name, target_doc=None):
	target_doc = get_mapped_doc("Maintenance Item", source_name,
		{"Maintenance Item": {
			"doctype": "Receive Maintenance Item",
			"field_map": {
				"name": "maintenance_item",
				"customer": "customer"
			}
		}}, target_doc)

	return target_doc

@frappe.whitelist()
def make_maintenance_order(source_name, target_doc=None):
        target_doc = get_mapped_doc("Maintenance Item", source_name,
                {"Maintenance Item": {
                        "doctype": "Maintenance Order",
                        "field_map": {
                                "name": "maintenance_item",
                                "customer": "customer"
                        }
                }}, target_doc)
        target_doc.warranty_bearing_rate=[]
        return target_doc


@frappe.whitelist()
def get_all_tolerence(self):
	from frappe.utils import add_to_date
	if self.warranty_template:
		warranty_data=frappe.get_doc("Warranty Template",self.warranty_template)
		if warranty_data.get("warranty_bearing_rate"):
			data_list=[]
			for tolerence in warranty_data.get("warranty_bearing_rate"):
				if float(tolerence.repairing_tolerance_item) >= 0.0 and float(tolerence.repairing_tolerance_services) >= 0.0:
					data={}
					if warranty_data.get("warranty_period_type")== "Days":
						if tolerence.idx == 1:
							data["warranty_start_date"]=self.warranty_start_date
							data["warranty_end_date"]=self.warranty_start_date
							data["repairing_tolerance_item"]= float(tolerence.repairing_tolerance_item)
							data["repairing_tolerance_services"]=tolerence.repairing_tolerance_services
							data["repair_tolerence"]=tolerence.repairing_tolerance
							data["full_warranty"]=tolerence.full_warranty
							
						else:
							data["warranty_start_date"]=add_to_date(self.warranty_start_date, days=tolerence.idx-1, as_string=True)
							data["warranty_end_date"]=add_to_date(self.warranty_start_date, days=tolerence.idx-1, as_string=True)
							data["repairing_tolerance_item"]= float(tolerence.repairing_tolerance_item)
							data["repairing_tolerance_services"]=tolerence.repairing_tolerance_services
							data["repair_tolerence"]=tolerence.repairing_tolerance
							data["full_warranty"]=tolerence.full_warranty
							
					elif warranty_data.get("warranty_period_type") == "Month":
						if tolerence.idx == 1:
							data["warranty_start_date"]=self.warranty_start_date
							data["warranty_end_date"]=add_to_date(frappe.utils.add_months(self.warranty_start_date, tolerence.idx), days=-1, as_string=True)
							data["repairing_tolerance_item"]= float(tolerence.repairing_tolerance_item)
							data["repairing_tolerance_services"]=tolerence.repairing_tolerance_services
							data["repair_tolerence"]=tolerence.repairing_tolerance
							data["full_warranty"]=tolerence.full_warranty
							
						else:
							data["warranty_start_date"]=frappe.utils.add_months(self.warranty_start_date, tolerence.idx-1)
							data["warranty_end_date"]=add_to_date(frappe.utils.add_months(self.warranty_start_date, tolerence.idx), days=-1, as_string=True)
							data["repairing_tolerance_item"]=float(tolerence.repairing_tolerance_item)
							data["repairing_tolerance_services"]=tolerence.repairing_tolerance_services
							data["repair_tolerence"]=tolerence.repairing_tolerance
							data["full_warranty"]=tolerence.full_warranty
							
					elif warranty_data.get("warranty_period_type") == "Year":
						if tolerence.idx == 1:
							data["warranty_start_date"]=self.warranty_start_date
							data["warranty_end_date"]=add_to_date(frappe.utils.add_months(self.warranty_start_date,12), days=-1, as_string=True)
							data["repair_tolerence"]=0 if tolerence.repairing_tolerance == 0 else tolerence.repairing_tolerance
							data["repairing_tolerance_item"]=0 if float(tolerence.repairing_tolerance_item) == 0.0 else tolerence.repairing_tolerance_item
							data["repairing_tolerance_services"]=0 if float(tolerence.repairing_tolerance_services) == 0.0 else tolerence.repairing_tolerance_services
							data["full_warranty"]=tolerence.full_warranty
							
						else:
							data["warranty_start_date"]=frappe.utils.add_months(self.warranty_start_date, (tolerence.idx*12)-12)
							data["warranty_end_date"]=add_to_date(frappe.utils.add_months(self.warranty_start_date, tolerence.idx*12), days=-1, as_string=True)
							data["repairing_tolerance_item"]=0 if float(tolerence.repairing_tolerance_item) == 0.0 else tolerence.repairing_tolerance_item
							data["repairing_tolerance_services"]=0 if float(tolerence.repairing_tolerance_services) == 0.0 else tolerence.repairing_tolerance_services
							data["repair_tolerence"]=0 if tolerence.repairing_tolerance == 0 else tolerence.repairing_tolerance
							data["full_warranty"]=tolerence.full_warranty
							
					data_list.append(data)
			self.warranty_bearing_rate=[]
			for tol in data_list:
				data=self.append("warranty_bearing_rate",{})
				data.repair_tolerence = tol["repair_tolerence"]
				data.repairing_tolerance_item = tol["repairing_tolerance_item"]
				data.repairing_tolerance_services = tol["repairing_tolerance_services"]
				data.warranty_start_date=tol["warranty_start_date"]
				data.warranty_end_date=tol["warranty_end_date"]
				data.full_warranty=tol["full_warranty"]
				
			
