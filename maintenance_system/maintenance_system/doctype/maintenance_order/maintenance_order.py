from __future__ import unicode_literals
import frappe
from frappe import msgprint
from frappe.model.document import Document
from frappe.utils import get_link_to_form, today
from frappe.model.mapper import get_mapped_doc


class MaintenanceOrder(Document):
    def validate(self):
        if not self.maintenance_order_added_by:
            self.maintenance_order_added_by = frappe.session.user
        
    def get_company(self):
        if self:
            get_company = frappe.get_doc("Maintenance System Settings")
            if get_company.company:
                # company_address=frappe.db.get_value("Dynamic Link",{"link_name":get_company.company,"link_doctype":"Company"},"parent")
                # self.company_address=company_address
                self.terms_and_conditions = get_company.terms_of_service
                if get_company.terms_of_service:
                    get_terms = frappe.get_doc(
                        "Terms and Conditions", get_company.terms_of_service)
                    self.terms = get_terms.terms
                self.company = get_company.company
            else:
                frappe.throw(
                    "Please Set a Default Company in Maintenance System Settings")

    def on_submit(self):
        if self.status == "Waiting":
            items = []
            for d in self.maintenance_malfunctions:
                item_li = {"malfunction": d.malfunction, "customer_note": d.customer_note,
                           "maintenance_notes": d.maintenance_notes}
                items.append(item_li)
            so = frappe.get_doc({
                "doctype": "Maintenance Directing",
                "customer": self.customer,
                "territory": self.territory,
                "issue_date": self.issue_date,
                "order_type": self.order_type,
                "maintenance_schedule": self.maintenance_schedule,
                "maintenance_end_date": self.maintenance_end_date,
                "maintenance_item": self.maintenance_item,
                "warranty_template": self.warranty_template,
                "warranty_status": self.warranty_status,
                "description": self.description,
                "accessories": self.accessories,
                "maintenance_malfunctions": items,
                "maintenance_order": self.name,
                "phone": self.phone,
                "mobile_no": self.mobile_no,
                "branch": self.branch,
                # "maintenance_team":self.maintenance_team,
                "maintenance_department": self.maintenance_department,
                "payment_method": self.payment_method,
                "warranty_start_date": self.warranty_start_date,
                "approval_to_add_items": self.approval_to_add_items,
                "contact": self.contact,
                "customer_address": self.customer_address,
                "address_display": self.address_display,
                "contact_display": self.contact_display,
                "phone": self.phone,
                "mobile_no": self.mobile_no,
                "total_amount": self.total_amount,
                "spare_part_quantity": self.total_quantity,
                "total_quantity": self.net_quantity,
                "service_total": self.service_total,
                "spare_part_total": self.total,
                "net_total": self.net_total,
                "kilometer": self.kilometer,
                "delivery_date": self.delivery_date,
                "tax_category": self.tax_category,
                "sales_taxes_and_charges_template": self.sales_taxes_and_charges_template,
                "total_taxes_and_charges": self.total_taxes_and_charges,
                "service_net_total": self.advance_paid,
                "outstanding_amount": self.outstanding_amount,
                "payment_received": self.payment_received

            })
            so.insert(ignore_permissions=True, ignore_mandatory=True)
            if self.warranty_bearing_rate:
                for rate in self.warranty_bearing_rate:
                    rate_append = so.append("warranty_bearing_rate", {})
                    rate_append.repair_tolerence = rate.repair_tolerence
                    rate_append.full_warranty = rate.full_warranty
                    rate_append.warranty_start_date = rate.warranty_start_date
                    rate_append.warranty_end_date = rate.warranty_end_date
            if self.table_60:
                for service in self.table_60:
                    service_item = so.append("maintenance_order_items", {})
                    service_item.maintenance_service = service.maintenance_service
                    service_item.maintenance_notes = service.maintenance_notes
                    service_item.price = service.price

            if self.table_66:
                for part in self.table_66:
                    spare_part = so.append("table_70", {})
                    spare_part.item_code = part.item_code
                    spare_part.qty = part.qty
                    spare_part.rate = part.rate
                    spare_part.amount = part.amount
                    spare_part.uom = part.uom
                    spare_part.delivery_date = part.delivery_date
                    spare_part.maintenance_engineer_notes = part.maintenance_engineer_notes
            if self.tax:
                for tax_rate in self.tax:
                    tax = so.append("tax", {})
                    tax.account_head = tax_rate.account_head
                    tax.cost_center = tax_rate.cost_center
                    tax.rate = tax_rate.rate
                    tax.tax_amount = tax_rate.tax_amount
                    tax.total = tax_rate.total
            so.save(ignore_permissions=True)
            frappe.msgprint("Maintenance Directing Created")
            self.status = "In Directing"
            self.save()
            frappe.clear_cache()
            frappe.db.set_value(self.doctype, self.name,
                                "maintenance_directing", so.name)
            self.reload()

        if self.receive_maintenance_items:
            sv = frappe.get_doc("Receive Maintenance Item",
                                self.receive_maintenance_items)
            sv.status = "Occupied"
            ct = sv.append("operations", {})
            ct.maintenance_order = self.name
            sv.save(ignore_permissions=True)
        if self.commission_benificiary:
            data_doc = frappe.new_doc("Maintenance Team Table")
            data_doc.parent = self.name
            data_doc.parenttype = self.doctype
            data_doc.parentfield = "table_90"
            data_doc.stages = self.doctype
            data_doc.team = self.commission_benificiary
            data_doc.insert()
            frappe.clear_cache()
            self.reload()
        else:
            data_doc = frappe.new_doc("Maintenance Team Table")
            data_doc.parent = self.name
            data_doc.parenttype = self.doctype
            data_doc.parentfield = "table_90"
            data_doc.stages = self.doctype
            data_doc.team = self.maintenance_team 
            data_doc.insert()
            frappe.clear_cache()
            self.reload()

    def on_cancel(self):
        if self.receive_maintenance_items:
            sv = frappe.get_doc("Receive Maintenance Item",
                                self.receive_maintenance_items)
            sv.status = "Available"
            for j in sv.operations:
                if j.maintenance_order == self.name:
                    sv.remove(j)
                    sv.save(ignore_permissions=True)
                else:
                    sv.save(ignore_permissions=True)


@frappe.whitelist(allow_guest=True)
def getPE(party):
    pe = frappe.db.sql("""select name, mode_of_payment, posting_date, unallocated_amount,paid_from,paid_to,cost_center,paid_amount  
			from `tabMaintenance Payment` where
			unallocated_amount > 0 and docstatus = 1 and party = %s;""", (party), as_list=1)
    return pe if pe else ""


@frappe.whitelist()
def get_branch(branch):
    if branch:
        maintenance_department = frappe.db.sql(
            f"""select parent from `tabMaintenance Department Branch` where branch = '{branch}' """, as_list=1)
        return maintenance_department if maintenance_department else ""


@frappe.whitelist(allow_guest=True)
def getDate(order_type, territory):
    date = frappe.db.sql("""select days from `tabMaintenance Schedule Territory`
                where parent = %s and territory = %s;""", (order_type, territory))
    return date


@frappe.whitelist(allow_guest=True)
def getIntrnalDate(order_type):
    date = frappe.db.sql("""select days from `tabMaintenance Schedule List`
                where name = %s;""", (order_type))
    return date


@frappe.whitelist()
def make_maintenance_processing(doc):
    m_order = frappe.get_doc('Maintenance Order', doc)
    items = []
    for d in m_order.maintenance_malfunctions:
        item_li = {"malfunction": d.malfunction}
        items.append(item_li)
    if m_order.status == "Waiting":
        so = frappe.get_doc({
            "doctype": "Maintenance Directing",
            "customer": m_order.customer,
            "territory": m_order.territory,
            "issue_date": m_order.issue_date,
            "order_type": m_order.order_type,
            "maintenance_schedule": m_order.maintenance_schedule,
            "maintenance_end_date": m_order.maintenance_end_date,
            "maintenance_item": m_order.maintenance_item,
            "warranty_template": m_order.warranty_template,
            "warranty_status": m_order.warranty_status,
            "description": m_order.description,
            "accessories": m_order.accessories,
            "maintenance_malfunctions": items,
            "maintenance_order": m_order.name,
            "branch": m_order.branch,
            # "maintenance_team":m_order.maintenance_team,
            "maintenance_department": m_order.maintenance_department,
            "payment_method": m_order.payment_method,
            "approval_to_add_items": m_order.approval_to_add_items,
            "contact": m_order.contact,
            "customer_address": m_order.customer_address,
            "address_display": m_order.address_display,
            "contact_display": m_order.contact_display,
            "phone": m_order.phone,
            "mobile_no": m_order.mobile_no
        })
        so.insert(ignore_permissions=True, ignore_mandatory=True)
        if m_order.warranty_bearing_rate:
            for rate in m_order.warranty_bearing_rate:
                rate_append = so.append("warranty_bearing_rate", {})
                rate_append.repair_tolerence = rate.repair_tolerence
                rate_append.full_warranty = rate.full_warranty
                rate_append.warranty_start_date = rate.warranty_start_date
                rate_append.warranty_end_date = rate.warranty_end_date

        if m_order.table_60:
            for service in m_order.table_60:
                service_item = so.append("maintenance_order_items", {})
                service_item.maintenance_service = service.maintenance_service
                service_item.price = service.price

        if m_order.table_66:
            for part in m_order.table_66:
                spare_part = so.append("table_70", {})
                spare_part.item_code = part.item_code
                spare_part.qty = part.qty
                spare_part.rate = part.rate
                spare_part.amount = part.amount
                spare_part.uom = part.uom
        so.save(ignore_permissions=True)
        frappe.msgprint("Maintenance Directing Created")


def maintenance_bearing(self):
    if self.maintenance_item:
        get_list = frappe.db.sql(f"""select name,full_warranty,repair_tolerence,warranty_start_date,warranty_end_date from `tabMaintenance Item Warranty Bearing` 
							where warranty_start_date <= Date('{self.creation}') and 
							warranty_end_date >= Date('{self.creation}') and parent = "{self.maintenance_item}";""", as_dict=1)

        if get_list:
            self.warranty_bearing_rate = []
            for item in get_list:
                data = self.append("warranty_bearing_rate", {})
                data.repair_tolerence = item["repair_tolerence"]
                data.warranty_start_date = item["warranty_start_date"]
                data.warranty_end_date = item["warranty_end_date"]
                data.full_warranty = item["full_warranty"]


@frappe.whitelist()
def get_address_name(ref_doctype, docname):
    # Return address name
    return get_party_address(ref_doctype, docname)


def get_party_address(doctype, name):
    out = frappe.db.sql(
        "SELECT dl.parent "
        "from `tabDynamic Link` dl join `tabAddress` ta on dl.parent=ta.name "
        "where "
        "dl.link_doctype=%s "
        "and dl.link_name=%s "
        "and dl.parenttype='Address' "
        "and ifnull(ta.disabled, 0) = 0 "
        "limit 1",
        (doctype, name),
    )
    if out:
        return out[0][0]
    else:
        return ""


@frappe.whitelist()
def get_contact_name(ref_doctype, docname):
    # Return Contact name
    return get_default_contact(ref_doctype, docname)


def get_default_contact(doctype, name):
    out = frappe.db.sql(
        """
			SELECT dl.parent, c.is_primary_contact, c.is_billing_contact
			FROM `tabDynamic Link` dl
			INNER JOIN `tabContact` c ON c.name = dl.parent
			WHERE
				dl.link_doctype=%s AND
				dl.link_name=%s AND
				dl.parenttype = 'Contact'
		""",
        (doctype, name),
    )
    if out:
        try:
            return out[0][0]
        except Exception:
            return None
    else:
        return None


@frappe.whitelist()
def default_branch():
    branch = frappe.db.get_value(
        "Branch", {"default_branch": 1, "enable": 1}, "name")
    return branch


@frappe.whitelist()
def order_default_branch(processing, doctype):
    if processing:
        m_order = frappe.db.get_value(
            doctype, {"name": processing}, "maintenance_order")
        if m_order:
            branch = frappe.db.get_value(
                "Maintenance Order", {"name": m_order}, "branch")
            if branch:
                return branch


@frappe.whitelist()
def get_company_address(company):
    if company:
        address = frappe.db.get_value(
            "Dynamic Link", {"link_doctype": "Company", "link_name": company}, "parent")
        return address
        
        
@frappe.whitelist()
def check_team(branch):
    cond = " and user='{0}'".format(frappe.session.user)
    if branch:
        cond += " and branch = '{0}' ".format(branch)
    get_data = frappe.db.sql(""" select name from `tabMaintenance Team` where enable=1 {0}""".format(cond))
    if get_data:
        return get_data
