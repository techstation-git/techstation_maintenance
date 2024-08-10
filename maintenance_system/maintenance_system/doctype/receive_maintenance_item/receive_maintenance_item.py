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

class ReceiveMaintenanceItem(Document):
        def before_submit(self):
                ritem = frappe.get_doc("Maintenance Item",self.maintenance_item)
                ritem.receive_maintenance_item = self.name
                ritem.save(ignore_permissions=True)
                self.create_barcode()

        def create_barcode(self):
                if self.create_barcode_automatically:
                        maintenance_setting=frappe.get_doc("Maintenance System Settings")
                        if maintenance_setting.get("generate_barcode_on_barcode_type"):
                                if maintenance_setting.get("item_barcode_type"):
                                        if maintenance_setting.get("item_barcode_type") == "CODE128":
                                                self.receive_maintenance_barcode = get_random_string(maintenance_setting.get("length"))
                                        elif maintenance_setting.get("item_barcode_type") == "EAN-13":
                                                self.receive_maintenance_barcode = get_random_number(12)
                                        elif maintenance_setting.get("item_barcode_type") == "UPC-A":
                                                self.receive_maintenance_barcode = get_random_number(11)
                                else:
                                        frappe.throw("Please Slect a Barcode Type for Genearete Barcode Automatically")
                        else:
                                if maintenance_setting.get("maintenance_item_barcode_series"):
                                        self.receive_maintenance_barcode=make_autoname(maintenance_setting.get("maintenance_item_barcode_series"))
                                else:
                                        frappe.throw("Please Set a Barcode Series For Generate Barcode Automatically")
                        frappe.msgprint("Barcode Generated Successfully")

import random
import string

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
def make_maintenance_order(source_name, target_doc=None):
        target_doc = get_mapped_doc("Receive Maintenance Item", source_name,
                {"Receive Maintenance Item": {
                        "doctype": "Maintenance Order",
                        "field_map": {
                                "maintenance_item": "maintenance_item",
                                "customer": "customer",
				"accessories": "accessories",
				"customer_notes": "description",
				"maintenance_malfunction": "maintenance_malfunction_item",
				"receive_maintenance_items": "name"
                        }
                }}, target_doc)

        return target_doc

