# -*- coding: utf-8 -*-
# Copyright (c) 2020, Tech Station and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import msgprint
from frappe.model.mapper import get_mapped_doc
from datetime import date
from frappe.model.document import Document

class MaintenanceDirecting(Document):
	def validate(self):
		if not self.current_stage:
			self.current_stage = 'Maintenance Directing'
		if not self.confirmed_by:
			self.confirmed_by = frappe.session.user
	def on_submit(self):
		frappe.db.set_value("Maintenance Order",self.maintenance_order,{"maintenance_directing":self.name,"status":"In Processing"})
		self.status = "In Processing"
		self.save()


		if self.order_type == "External":
			so = frappe.get_doc({
			"doctype": "External Processing",
			"customer": self.customer,
			"territory": self.territory,
			"maintenance_invoice":"",
			"issue_date": self.issue_date,
			"order_type": self.order_type,
			"delivery_type": self.delivery_type,
			"maintenance_schedule": self.maintenance_schedule,
			"maintenance_end_date": self.maintenance_end_date,
			"receive_maintenance_items": self.receive_maintenance_items,
			"maintenance_item": self.maintenance_item,
			"maintenance_department": self.maintenance_department,
			"maintenance_support_car": self.maintenance_support_car,
			"warranty_template": self.warranty_template,
			"customer_tolerance": self.customer_tolerance,
			"warranty_status": self.warranty_status,
			"warranty_expiry_date": self.warranty_expiry_date,
			"notes_on_warranty": self.notes_on_warranty,
			"description": self.description,
			"accessories": self.accessories,
			"maintenance_malfunctions": self.maintenance_malfunctions,
            		"kilometer":self.kilometer,
			"service_total": self.service_total,
			"service_net_total": self.service_net_total,
			"grand_total": self.total_amount,
			"net_grand_total": self.service_net_total,
			"maintenance_order": self.maintenance_order,
			"maintenance_directing": self.name,
			"preferred_method_of_communication": self.preferred_method_of_communication,
			"phone": self.phone,
			"mobile_no": self.mobile_no,
			"mobile_no_1": self.mobile_no_1,
			"mobile_no_2": self.mobile_no_2,
			"mobile_no_3": self.mobile_no_3,
			"watsapp": self.watsapp,
			"telegram": self.telegram,
			"address": self.address,
			"citytown": self.citytown,
			"street": self.street,
			"country": self.country,
			"postal_code": self.postal_code,
			"house_number": self.house_number,
			"apartment_number": self.apartment_number,
			"floor": self.floor,
			"way_to_climb": self.way_to_climb,
			"special_marque": self.special_marque,
			"branch":self.branch,
			"maintenance_team":self.maintenance_team,
			"maintenance_department":self.maintenance_department,
			"payment_method":self.payment_method,
			"warranty_start_date":self.warranty_start_date,
			"approval_to_add_items":self.approval_to_add_items,
			"contact":self.contact,
			"customer_address":self.customer_address,
			"address_display":self.address_display,
			"contact_display":self.contact_display,
			"phone":self.phone,
			"mobile_no":self.mobile_no,
			"spare_part_quantity":self.total_quantity,
			"total_quantity":self.total_quantity,
			"service_total":self.service_total,
			"spare_part_total":self.spare_part_total,
			"net_total":self.net_total,
			"tax_category":self.tax_category,
			"sales_taxes_and_charges_template":self.sales_taxes_and_charges_template,
			"total_taxes_and_charges":self.total_taxes_and_charges,
			"service_net_total":self.service_net_total,
			"outstanding_amount":self.outstanding_amount,
            "delivery_date":self.delivery_date,
            "payment_received":self.payment_received
			})
			so.insert(ignore_permissions=True,ignore_mandatory=True)
			if self.maintenance_order_items:
				for item in self.maintenance_order_items:
					data=so.append("services",{})
					data.maintenance_service=item.maintenance_service
					data.price=item.price
					data.maintenance_notes=item.maintenance_notes
					data.flags.ignore_mandatory=True
			if self.warranty_bearing_rate:
				for rate in self.warranty_bearing_rate:
					rate_append=so.append("warranty_bearing_rate",{})
					rate_append.repair_tolerence=rate.repair_tolerence
					rate_append.full_warranty=rate.full_warranty
					rate_append.warranty_start_date=rate.warranty_start_date
					rate_append.warranty_end_date=rate.warranty_end_date
			if self.table_70:
				for part in self.table_70:
					spare_part=so.append("table_68",{})
					spare_part.item_code=part.item_code
					spare_part.qty=part.qty
					spare_part.rate=part.rate
					spare_part.amount=part.amount
					spare_part.uom=part.uom
					spare_part.delivery_date=part.delivery_date
					spare_part.maintenance_engineer_notes=part.maintenance_engineer_notes
			if self.tax:
				for tax_rate in self.tax:
					tax=so.append("tax",{})
					tax.account_head=tax_rate.account_head
					tax.cost_center=tax_rate.cost_center
					tax.rate=tax_rate.rate
					tax.tax_amount=tax_rate.tax_amount
					tax.total=tax_rate.total
			so.save(ignore_permissions=True)
			self.db_set("external_processing",so.name)
			frappe.msgprint("External Processing Created")


		if self.order_type == "Internal":
			so = frappe.get_doc({
			"doctype": "Internal Processing",
			"customer": self.customer,
			"territory": self.territory,
			"issue_date": self.issue_date,
			"order_type": self.order_type,
			"maintenance_invoice":"",
			"delivery_type": self.delivery_type,
			"maintenance_schedule": self.maintenance_schedule,
			"maintenance_end_date": self.maintenance_end_date,
			"receive_maintenance_items": self.receive_maintenance_items,
			"maintenance_item": self.maintenance_item,
			"maintenance_department": self.maintenance_department,
			"maintenance_team": self.maintenance_team,
			"warranty_template": self.warranty_template,
			"customer_tolerance": self.customer_tolerance,
			"warranty_status": self.warranty_status,
			"warranty_expiry_date": self.warranty_expiry_date,
			"notes_on_warranty": self.notes_on_warranty,
			"description": self.description,
			"accessories": self.accessories,
			"maintenance_malfunctions": self.maintenance_malfunctions,
			"service_total": self.service_total,
			"service_net_total": self.service_net_total,
			"grand_total": self.total_amount,
			"net_grand_total": self.service_net_total,
			"maintenance_order": self.maintenance_order,
			"maintenance_directing": self.name,
			"preferred_method_of_communication": self.preferred_method_of_communication,
			"phone": self.phone,
            		"kilometer":self.kilometer,
			"mobile_no": self.mobile_no,
			"mobile_no_1": self.mobile_no_1,
			"mobile_no_2": self.mobile_no_2,
			"mobile_no_3": self.mobile_no_3,
			"watsapp": self.watsapp,
			"telegram": self.telegram,
			"address": self.address,
			"citytown": self.citytown,
			"street": self.street,
			"country": self.country,
			"postal_code": self.postal_code,
			"house_number": self.house_number,
			"apartment_number": self.apartment_number,
			"floor": self.floor,
			"way_to_climb": self.way_to_climb,
			"special_marque": self.special_marque,
			"branch":self.branch,
			"maintenance_department":self.maintenance_department,
			"payment_method":self.payment_method,
			"warranty_start_date":self.warranty_start_date,
			"approval_to_add_items":self.approval_to_add_items,
			"contact":self.contact,
			"customer_address":self.customer_address,
			"address_display":self.address_display,
			"contact_display":self.contact_display,
			"phone":self.phone,
			"mobile_no":self.mobile_no,
			"spare_part_quantity":self.total_quantity,
			"total_quantity":self.total_quantity,
			"service_total":self.service_total,
			"spare_part_total":self.spare_part_total,
			"net_total":self.net_total,
			"tax_category":self.tax_category,
			"sales_taxes_and_charges_template":self.sales_taxes_and_charges_template,
			"total_taxes_and_charges":self.total_taxes_and_charges,
			"service_net_total":self.service_net_total,
			"outstanding_amount":self.outstanding_amount,
            "delivery_date":self.delivery_date,
            "payment_received":self.payment_received
			})
			so.insert(ignore_permissions=True,ignore_mandatory=True)
			if self.maintenance_order_items:
				for item in self.maintenance_order_items:
					data=so.append("services",{})
					data.maintenance_service=item.maintenance_service
					data.price=item.price
					data.maintenance_notes=item.maintenance_notes
					data.flags.ignore_mandatory=True
			if self.warranty_bearing_rate:
				for rate in self.warranty_bearing_rate:
					rate_append=so.append("warranty_bearing_rate",{})
					rate_append.repair_tolerence=rate.repair_tolerence
					rate_append.full_warranty=rate.full_warranty
					rate_append.warranty_start_date=rate.warranty_start_date
					rate_append.warranty_end_date=rate.warranty_end_date
			if self.table_70:
				for part in self.table_70:
					spare_part=so.append("table_67",{})
					spare_part.item_code=part.item_code
					spare_part.qty=part.qty
					spare_part.rate=part.rate
					spare_part.amount=part.amount
					spare_part.uom=part.uom
					spare_part.delivery_date=part.delivery_date
					spare_part.maintenance_engineer_notes=part.maintenance_engineer_notes
			if self.tax:
				for tax_rate in self.tax:
					tax=so.append("tax",{})
					tax.account_head=tax_rate.account_head
					tax.cost_center=tax_rate.cost_center
					tax.rate=tax_rate.rate
					tax.tax_amount=tax_rate.tax_amount
					tax.total=tax_rate.total
			so.save(ignore_permissions=True)
			self.db_set("internal_processing",so.name)
			frappe.msgprint("Internal Processing Created")
        
		team_list=[]
		if self.maintenance_order:
			or_doc=frappe.get_doc("Maintenance Order",self.maintenance_order)
			if or_doc.table_90:
				for item in or_doc.table_90:
					dict1={}
					dict1["stages"]=item.stages
					dict1["team"]=item.team
					team_list.append(dict1)
		if self.commission_benificiary:
			data_doc = {}
			data_doc["stages"]=self.doctype
			data_doc["team"]=self.commission_benificiary
			team_list.append(data_doc)
		else:
			data_doc = {}
			data_doc["stages"]=self.doctype
			data_doc["team"]=self.maintenance_team
			team_list.append(data_doc)
		if team_list:
			for data in team_list:
				data_doc1=frappe.new_doc("Maintenance Team Table")
				data_doc1.parent=self.name
				data_doc1.parenttype=self.doctype
				data_doc1.parentfield="table_103"
				data_doc1.stages=data.get("stages")
				data_doc1.team=data.get("team")
				data_doc1.insert()
			frappe.clear_cache()
			self.reload()


	def on_cancel(self):
		mo = frappe.get_doc("Maintenance Order",self.maintenance_order)
		mo.status = "Waiting"
		mo.maintenance_directing = "undefined"
		mo.save(ignore_permissions=True)

@frappe.whitelist(allow_guest=True)
def getPrice(item_code):
    ms_setting=frappe.get_doc("Maintenance System Settings")
    if ms_setting.default_price_list:
        price_list=ms_setting.default_price_list
        mt = frappe.db.sql("""select price_list_rate,uom from `tabItem Price` where selling = 1 and price_list= %s and item_code = %s ORDER BY creation
                DESC LIMIT 1 ;""",(price_list,item_code),as_list=1)
        return mt if mt else ""
    else:
        return ""
