# -*- coding: utf-8 -*-
# Copyright (c) 2020, Tech Station and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import msgprint
from frappe.model.mapper import get_mapped_doc
from datetime import date
from frappe.model.document import Document


class InternalProcessing(Document):
    def validate(self):
        if not self.current_stage:
            self.current_stage = 'Internal Processing'
        if not self.confirmed_by:
            self.confirmed_by = frappe.session.user
        
        # Phase 2: Custody Management - Check if custody is returned before completion
        self.validate_custody_before_completion()
    
    def validate_custody_before_completion(self):
        """Ensure custody is returned before completing processing"""
        if self.maintenance_order and self.status == "Complete":
            # Get the maintenance order
            mo = frappe.get_doc("Maintenance Order", self.maintenance_order)
            
            if mo.custody_issued and mo.custody_status not in ["Fully Returned", "Not Issued"]:
                frappe.throw(
                    f"Cannot complete processing. Custody items are still <b>{mo.custody_status}</b>. "
                    f"Please return all custody items first.<br><br>"
                    f"Custody Record: {frappe.utils.get_link_to_form('Technician Custody', mo.linked_custody)}",
                    title="Custody Not Returned"
                )
    def on_submit(self):
        if self.maintenance_directing:
            mo = frappe.get_doc("Maintenance Directing",
                                self.maintenance_directing)
            mo.status = "In Processing"
            mo.approval_to_add_items = self.approval_to_add_items
            mo.save(ignore_permissions=True)
        team_list = []

        if not self.table_115:
            if self.maintenance_order:
                or_doc = frappe.get_doc(
                    "Maintenance Directing", self.maintenance_directing)
                if or_doc.table_103:
                    for item in or_doc.table_103:
                        dict1 = {}
                        dict1["stages"] = item.stages
                        dict1["team"] = item.team
                        team_list.append(dict1)
        if self.commission_benificiary:
            data_doc = {}
            data_doc["stages"] = self.doctype
            data_doc["team"] = self.commission_benificiary
            team_list.append(data_doc)
        else:
            data_doc = {}
            data_doc["stages"] = self.doctype
            data_doc["team"] = self.maintenance_team
            team_list.append(data_doc)
        if team_list:
            for data in team_list:
                data_doc1 = frappe.new_doc("Maintenance Team Table")
                data_doc1.parent = self.name
                data_doc1.parenttype = self.doctype
                data_doc1.parentfield = "table_115"
                data_doc1.stages = data.get("stages")
                data_doc1.team = data.get("team")
                data_doc1.insert()
            frappe.clear_cache()
            self.reload()
 
    def on_update_after_submit(self):
        get_invoice = frappe.db.sql("""select name from `tabMaintenance Invoice` where docstatus = 0 and processing=%s
                      and processing_type = 'Internal Processing' """,(str(self.name)))
        if get_invoice:
            make_maintenance_invoice(self.name, invoice_name = get_invoice[0][0])

@frappe.whitelist()
def make_maintenance_products_receipt(source_name, target_doc=None):
    target_doc = get_mapped_doc("Internal Processing", source_name,
                                {"Internal Processing": {
                                    "doctype": "Maintenance Material Receipt",
                                    "field_map": {
                                        "doctype": "processing_type",
                                        "name": "processing",
                                        "customer": "customer"
                                    }
                                }}, target_doc)

    return target_doc


@frappe.whitelist()
def make_maintenance_invoice(doc, invoice_name = None):
    minv = frappe.get_doc('Internal Processing', doc)
    qtys = qty(minv)
    calculate_totals = calculate_total(minv)
    so = frappe.get_doc({
        "doctype": "Maintenance Invoice",
        "customer": minv.customer,
        "posting_date": minv.issue_date,
        "warranty_template": minv.warranty_template,
        "customer_tolerance": minv.customer_tolerance,
        "warranty_status": minv.warranty_status,
        "warranty_expiry_date": minv.warranty_expiry_date,
        "notes_on_warranty": minv.notes_on_warranty,
        "get_advance_payment": minv.get_advance_payment,
        "maintenance_advance_payment": minv.maintenance_advance_payment,
        "receive_maintenance_items": minv.receive_maintenance_items,
        "maintenance_item": minv.maintenance_item,
        "maintenance_department": minv.maintenance_department,
        "maintenance_team": minv.maintenance_team,
        "maintenance_order": minv.maintenance_order,
        "processing_type": "Internal Processing",
        "processing": doc,
        "maintenance_directing": minv.maintenance_directing,
        "preferred_method_of_communication": minv.preferred_method_of_communication,
        "phone": minv.phone,
        "mobile_no": minv.mobile_no,
        "mobile_no_1": minv.mobile_no_1,
        "mobile_no_2": minv.mobile_no_2,
        "mobile_no_3": minv.mobile_no_3,
        "watsapp": minv.watsapp,
        "telegram": minv.telegram,
        "address": minv.address,
        "citytown": minv.citytown,
        "street": minv.street,
        "country": minv.country,
        "contact": minv.contact,
        "kilometer": minv.kilometer,
        "customer_address": minv.customer_address,
        "postal_code": minv.postal_code,
        "house_number": minv.house_number,
        "apartment_number": minv.apartment_number,
        "floor": minv.floor,
        "way_to_climb": minv.way_to_climb,
        "special_marque": minv.special_marque,
        "approval_to_add_items": minv.approval_to_add_items,
        "branch": minv.branch,
        "payment_method": minv.payment_method,
        "territory": minv.territory,
        "order_type": minv.order_type,
        "address_display": minv.address_display,
        "contact_display": minv.contact_display,
        "phone": minv.phone,
        "mobile_no": minv.mobile_no,
        "delivery_date": minv.delivery_date,
        "company": minv.company,
        "currency": minv.currency,
        "price_list": minv.price_list,
        "tax_category": minv.tax_category,
        "sales_taxes_and_charges_template": minv.sales_taxes_and_charges_template,
        "payment_received": minv.payment_received,
        "total_qty": qtys.get("total_qty"),
        "spare_part_quantity": qtys.get("spare_part_quantity"),
        "service_total": calculate_totals.get("service_total"),
        "total_amount": calculate_totals.get("total_amount"),
        "service_net_total": calculate_totals.get("service_net_total"),
        "total_taxes_and_charges": calculate_totals.get("total_taxes_and_charges"),
        "grand_total": calculate_totals.get("grand_total"),
        "paid_amount": calculate_totals.get("outstanding_amount"),
        "outstanding_amount": calculate_totals.get("paid_amount"),
    })
    if invoice_name:
        so = frappe.get_doc('Maintenance Invoice', invoice_name)
    else:
    	so.insert(ignore_permissions=True, ignore_mandatory=True)
    if minv.spare_parts:
        for item in minv.spare_parts:
            data = so.append("items", {})
            data.item_code = item.item_code
            data.qty = item.qty
            data.rate = item.rate
            data.amount = item.amount
            data.uom = item.uom
            data.delivery_date = minv.delivery_date
            data.flags.ignore_mandatory = True
    if minv.services:
        so.service = []
        for item in minv.services:
            data = so.append("service", {})
            data.maintenance_service = item.maintenance_service
            data.price = item.price
            data.flags.ignore_mandatory = True
    if minv.warranty_bearing_rate:
        for rate in minv.warranty_bearing_rate:
            rate_append = so.append("warranty_bearing_rate", {})
            rate_append.repair_tolerence = rate.repair_tolerence
            rate_append.full_warranty = rate.full_warranty
            rate_append.warranty_start_date = rate.warranty_start_date
            rate_append.warranty_end_date = rate.warranty_end_date
    if calculate_totals.get("tax_list"):
        for rate in calculate_totals.get("tax_list"):
            rate_append = so.append("tax", {})
            rate_append.account_head = rate.get("account_head")
            rate_append.cost_center = rate.get("cost_center")
            rate_append.rate = rate.get("rate")
            rate_append.tax_amount = rate.get("tax_amount")
            rate_append.total = rate.get("total")
    
    so.flags.ignore_mandatory = True
    so.save(ignore_permissions=True)
    if invoice_name:
        msgprint("Maintenance Invoice Updated")
    else:
        minv.db_set("maintenance_invoice", so.name)
        msgprint("Maintenance Invoice Created")


def calculate_total(minv):
    service_total = spare_part_total = net_total = 0
    tax_total = grand_total = paid_amount = outstanding_amount = 0
    tax_list = []
    if minv.spare_parts:
        for amount in minv.spare_parts:
            spare_part_total += float(amount.qty)*float(amount.rate)
    if minv.services:
        for amount in minv.services:
            service_total += float(amount.price)
    net_total = spare_part_total+service_total
    if minv.tax:
        for amount in minv.tax:
            tax_total += net_total*(amount.rate/100)
            tax_row = {}
            tax_row["account_head"] = amount.account_head
            tax_row["cost_center"] = amount.cost_center
            tax_row["rate"] = amount.rate
            tax_row["tax_amount"] = float(net_total)*(amount.rate/100)
            tax_row["total"] = float(net_total)+(net_total*(amount.rate/100))
            tax_list.append(tax_row)
    grand_total = net_total+tax_total
    # frappe.msgprint(str(grand_total))
    return {"service_total": service_total,
            "total_amount": spare_part_total,
            "service_net_total": net_total,
            "total_taxes_and_charges": tax_total,
            "grand_total": grand_total,
            "paid_amount": grand_total,
            "outstanding_amount": outstanding_amount,
            "tax_list": tax_list
            }


def qty(minv):
    total_qty = 0
    if minv.spare_parts:
        for qty in minv.spare_parts:
            total_qty += qty.qty
    return {"total_qty": total_qty, "spare_part_quantity": total_qty}


@frappe.whitelist()
def update_all_document(doc, doctype, status):
    if doc:
        m_direct = frappe.get_doc(doctype, doc)
        frappe.db.set_value("Maintenance Directing",
                            m_direct.maintenance_directing, {"status": status})
        m_order = frappe.get_doc(
            "Maintenance Directing", m_direct.maintenance_directing)
        frappe.db.set_value("Maintenance Order",
                            m_order.maintenance_order, {"status": status})
