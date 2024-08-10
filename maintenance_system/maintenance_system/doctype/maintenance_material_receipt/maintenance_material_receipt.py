# -*- coding: utf-8 -*-
# Copyright (c) 2020, Tech Station and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from datetime import date
from frappe import msgprint
from frappe.model.document import Document

class MaintenanceMaterialReceipt(Document):
	def on_submit(self):
		self.delivered_by=frappe.session.user
		if self.processing_type == "Internal Processing":
			mp = frappe.get_doc("Internal Processing",self.processing)
			mp.maintenance_products_receipt = self.name
			mp.status = "Delivered"
			mp.material_total += self.total
			mp.grand_total += self.total

			for i in self.items:
				item_li = {"item_code": i.item_code,"delivery_date":mp.delivery_date,"qty": i.qty,"rate": i.rate,"amount":i.amount,"uom": i.uom}
				ct = mp.append("spare_parts",item_li)
			mp.save(ignore_permissions=True)

		if self.processing_type == "External Processing":
			mp = frappe.get_doc("External Processing",self.processing)
			mp.maintenance_products_receipt = self.name
			mp.status = "Delivered"
			mp.material += self.total
			mp.grand_total += self.total
			if mp.warranty_type == "Item" or mp.warranty_type == "Item and Service":
				mp.material_net_total += self.total * (mp.customer_tolerance / 100)
				mp.net_grand_total += self.total * (mp.customer_tolerance / 100)
			else:
				mp.material_net_total += self.total
				mp.net_grand_total += self.total
			for i in self.items:
				item_li = {"item_code": i.item_code,"delivery_date":mp.delivery_date,"qty": i.qty,"rate": i.rate,"amount":i.amount,"uom": i.uom}
				ct = mp.append("spare_parts",item_li)
			mp.save(ignore_permissions=True)


		items = []
		for d in self.items:
			item_li = {"item_code": d.item_code,"qty": d.qty,"uom":d.uom,"basic_rate": d.rate,"basic_amount":d.amount,"s_warehouse":self.warehouse}
			items.append(item_li)

		dn = frappe.get_doc({
		"doctype": "Stock Entry",
		"stock_entry_type": "Material Issue",
		"from_warehouse": self.warehouse,
		"posting_date": date.today(),
		"maintenance_material_receipt": self.name,
		"items": items
		})
		dn.insert(ignore_permissions=True)
		dn.save(ignore_permissions=True)
		dn.submit()
		self.status = "Delivered"
		self.save()
		msgprint("Stock Entry Created")

	def on_cancel(self):
		st = frappe.db.get_value("Stock Entry", {"maintenance_products_receipt": self.name})
		stock = frappe.get_doc("Stock Entry",st)
		stock.cancel()
		stock.delete()

		mp = frappe.get_doc("Maintenance Processing",self.maintenance_processing)
		mp.maintenance_products_receipt = "undefined"
		if mp.maintenance_invoice == "undefined":
			mp.status = "Complete"
			mp.save(ignore_permissions=True)

		if mp.maintenance_invoice != "undefined":
			mp.status = "Start"
			mp.save(ignore_permissions=True)


# @frappe.whitelist()
# def get_warehouse():
# 	user=frappe.session.user
# 	if user:
# 		warehouse=frappe.db.get_value("Maintenance Team",{"user":user,"enable":1},"warehouse")
# 		return warehouse


@frappe.whitelist()
def update_actual(item_code,warehouse):
    if item_code:
        bin_list=frappe.db.get_value("Bin",{"item_code":item_code,"warehouse":warehouse},"actual_qty")
        return bin_list
