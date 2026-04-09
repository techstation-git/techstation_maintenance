import frappe
from frappe import _

def cascade_cancel(doc, method=None):
    """Cascade cancellation to all linked documents."""
    if frappe.flags.in_maintenance_sync:
        return

    frappe.flags.in_maintenance_sync = True
    try:
        # Define linked fields to check for each DocType
        link_map = {
            "Maintenance Order": [
                "sales_order", "maintenance_directing", "maintenance_invoice", 
                "maintenance_payment", "maintenance_material_receipt", 
                "internal_processing", "external_processing"
            ],
            "Maintenance Directing": [
                "internal_processing", "external_processing", "maintenance_order"
            ],
            "External Processing": ["maintenance_directing", "maintenance_order"],
            "Internal Processing": ["maintenance_directing", "maintenance_order"],
            "Maintenance Invoice": ["maintenance_order"],
            "Maintenance Payment": ["maintenance_invoice"],
            "Sales Order": ["maintenance_order"]
        }

        linked_fields = link_map.get(doc.doctype, [])
        
        # 1. Handle explicit links in this document
        for fieldname in linked_fields:
            target_val = doc.get(fieldname)
            if target_val and target_val != "undefined":
                # Guess linked DocType if not explicit
                target_dt = fieldname.replace("_", " ").title()
                if fieldname == "sales_order":
                    target_dt = "Sales Order"
                elif fieldname == "maintenance_order":
                    target_dt = "Maintenance Order"
                
                if frappe.db.exists(target_dt, target_val):
                    target_doc = frappe.get_doc(target_dt, target_val)
                    if target_doc.docstatus == 1:
                        # Unlink to avoid circularity errors during cancel
                        doc.db_set(fieldname, None)
                        target_doc.cancel()

        # 2. Handle reverse links (where this doc is mentioned in others)
        if doc.doctype == "Sales Order":
            # Find all MOs linked to this SO
            mos = frappe.get_all("Maintenance Order", filters={"sales_order": doc.name, "docstatus": 1})
            for mo_info in mos:
                mo = frappe.get_doc("Maintenance Order", mo_info.name)
                mo.cancel()
        
        elif doc.doctype == "Maintenance Order":
            # Find any other docs that might link to this MO but aren't in the explicit fields
            # (e.g. docs created *from* MO but not linked back in MO fields)
            for dt in ["Maintenance Directing", "Maintenance Invoice", "External Processing", "Internal Processing"]:
                links = frappe.get_all(dt, filters={"maintenance_order": doc.name, "docstatus": 1})
                for link in links:
                    frappe.get_doc(dt, link.name).cancel()

    finally:
        frappe.flags.in_maintenance_sync = False

def cascade_delete(doc, method=None):
    """Cascade deletion to all linked documents."""
    if frappe.flags.in_maintenance_sync:
        return

    frappe.flags.in_maintenance_sync = True
    try:
        # Similar logic for deletion
        link_map = {
            "Maintenance Order": [
                "sales_order", "maintenance_directing", "maintenance_invoice", 
                "maintenance_payment", "maintenance_material_receipt", 
                "internal_processing", "external_processing"
            ],
            "Maintenance Directing": [
                "internal_processing", "external_processing"
            ],
            "Sales Order": ["maintenance_order"]
        }

        linked_fields = link_map.get(doc.doctype, [])
        
        for fieldname in linked_fields:
            target_val = doc.get(fieldname)
            if target_val and target_val != "undefined":
                target_dt = fieldname.replace("_", " ").title()
                if fieldname == "sales_order":
                    target_dt = "Sales Order"
                elif fieldname == "maintenance_order":
                    target_dt = "Maintenance Order"
                
                if frappe.db.exists(target_dt, target_val):
                    target_doc = frappe.get_doc(target_dt, target_val)
                    # Unlink to avoid circularity errors during delete
                    doc.db_set(fieldname, None)
                    if target_doc.docstatus == 2:
                        target_doc.delete()
                    elif target_doc.docstatus == 0:
                        target_doc.delete()

        # Reverse links
        if doc.doctype == "Sales Order":
            mos = frappe.get_all("Maintenance Order", filters={"sales_order": doc.name})
            for mo_info in mos:
                frappe.delete_doc("Maintenance Order", mo_info.name, ignore_permissions=True)
        elif doc.doctype == "Maintenance Order":
            for dt in ["Maintenance Directing", "Maintenance Invoice", "External Processing", "Internal Processing"]:
                links = frappe.get_all(dt, filters={"maintenance_order": doc.name})
                for link in links:
                    frappe.delete_doc(dt, link.name, ignore_permissions=True)

    finally:
        frappe.flags.in_maintenance_sync = False
