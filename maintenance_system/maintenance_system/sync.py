import frappe
from frappe import _

def cascade_cancel(doc, method=None):
    """Cascade cancellation to all linked documents."""
    # Use a set to track docs currently being processed in this request to allow nested cascades
    # but prevent infinite loops (circular references)
    if not hasattr(frappe.local, "maintenance_sync_processing"):
        frappe.local.maintenance_sync_processing = set()
    
    doc_id = (doc.doctype, doc.name)
    if doc_id in frappe.local.maintenance_sync_processing:
        return

    frappe.local.maintenance_sync_processing.add(doc_id)
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
                    try:
                        target_doc = frappe.get_doc(target_dt, target_val)
                        if target_doc.docstatus == 1:
                            # Unlink to avoid circularity errors during cancel
                            doc.db_set(fieldname, None)
                            target_doc.flags.ignore_links = True
                            target_doc.cancel()
                    except Exception as e:
                        frappe.log_error(f"Error cascading cancel to {target_dt} {target_val}: {str(e)}", "Cascade Cancel")

        # 2. Handle reverse links (where this doc is mentioned in others)
        if doc.doctype == "Sales Order":
            # Find all MOs linked to this SO
            mos = frappe.get_all("Maintenance Order", filters={"sales_order": doc.name, "docstatus": 1})
            for mo_info in mos:
                try:
                    mo = frappe.get_doc("Maintenance Order", mo_info.name)
                    mo.flags.ignore_links = True
                    mo.cancel()
                except Exception as e:
                    frappe.log_error(f"Error cascading cancel to Maintenance Order {mo_info.name}: {str(e)}", "Cascade Cancel")
        
        elif doc.doctype == "Maintenance Order":
            # Find any other docs that might link to this MO but aren't in the explicit fields
            # (e.g. docs created *from* MO but not linked back in MO fields)
            for dt in ["Maintenance Directing", "Maintenance Invoice", "External Processing", "Internal Processing", "Maintenance Payment"]:
                try:
                    links = frappe.get_all(dt, filters={"maintenance_order": doc.name, "docstatus": 1})
                    for link in links:
                        try:
                            # Unlink from parent first to avoid link validation errors
                            frappe.db.set_value(dt, link.name, "maintenance_order", None, update_modified=False)
                            target = frappe.get_doc(dt, link.name)
                            target.flags.ignore_links = True
                            target.cancel()
                        except Exception as e:
                            frappe.log_error(f"Error cascading cancel to {dt} {link.name}: {str(e)}", "Cascade Cancel")
                except Exception as e:
                    frappe.log_error(f"Error fetching {dt} linked to {doc.name}: {str(e)}", "Cascade Cancel")
            
            # Also cancel linked Sales Order and Sales Invoices
            try:
                sales_order = doc.get("sales_order")
                if sales_order and frappe.db.exists("Sales Order", sales_order):
                    so = frappe.get_doc("Sales Order", sales_order)
                    if so.docstatus == 1:
                        so.flags.ignore_links = True
                        so.cancel()
            except Exception as e:
                frappe.log_error(f"Error cascading cancel to Sales Order: {str(e)}", "Cascade Cancel")
            
            # Find and cancel any Sales Invoices linked to this Maintenance Order
            try:
                sales_invoices = frappe.get_all("Sales Invoice", filters={"maintenance_order": doc.name, "docstatus": 1})
                for si_info in sales_invoices:
                    try:
                        si = frappe.get_doc("Sales Invoice", si_info.name)
                        si.flags.ignore_links = True
                        si.cancel()
                    except Exception as e:
                        frappe.log_error(f"Error cascading cancel to Sales Invoice {si_info.name}: {str(e)}", "Cascade Cancel")
            except Exception as e:
                frappe.log_error(f"Error fetching Sales Invoices linked to {doc.name}: {str(e)}", "Cascade Cancel")

    finally:
        frappe.local.maintenance_sync_processing.remove(doc_id)

def cascade_delete(doc, method=None):
    """Cascade deletion to all linked documents.
    
    Process:
    1. First cancel all submitted linked documents (to clear links safely)
    2. Then delete all linked documents (both submitted and draft)
    """
    if not hasattr(frappe.local, "maintenance_sync_processing"):
        frappe.local.maintenance_sync_processing = set()
    
    doc_id = (doc.doctype, doc.name)
    if doc_id in frappe.local.maintenance_sync_processing:
        return

    frappe.local.maintenance_sync_processing.add(doc_id)
    try:
        # Define DocTypes to cascade delete based on document type
        cascade_map = {
            "Maintenance Order": [
                "Maintenance Directing", "Maintenance Invoice", 
                "External Processing", "Internal Processing", "Maintenance Payment",
                "Sales Order", "Sales Invoice"
            ],
            "Maintenance Directing": [
                "External Processing", "Internal Processing"
            ],
            "Sales Order": ["Maintenance Order", "Sales Invoice"]
        }

        cascade_list = cascade_map.get(doc.doctype, [])
        
        # Step 1: Cancel all submitted linked documents first
        if doc.doctype == "Maintenance Order":
            # Cancel linked Maintenance Directing, Invoice, etc.
            for dt in ["Maintenance Directing", "Maintenance Invoice", "External Processing", "Internal Processing", "Maintenance Payment"]:
                try:
                    links = frappe.get_all(dt, filters={"maintenance_order": doc.name, "docstatus": 1})
                    for link in links:
                        try:
                            target = frappe.get_doc(dt, link.name)
                            target.flags.ignore_links = True
                            target.cancel()
                        except Exception as e:
                            frappe.log_error(f"Error canceling {dt} {link.name} during cascade delete: {str(e)}", "Cascade Delete")
                except Exception as e:
                    frappe.log_error(f"Error fetching {dt} linked to {doc.name}: {str(e)}", "Cascade Delete")
            
            # Cancel linked Sales Order
            try:
                sales_order = doc.get("sales_order")
                if sales_order and frappe.db.exists("Sales Order", sales_order):
                    so = frappe.get_doc("Sales Order", sales_order)
                    if so.docstatus == 1:
                        so.flags.ignore_links = True
                        so.cancel()
            except Exception as e:
                frappe.log_error(f"Error canceling Sales Order during cascade delete: {str(e)}", "Cascade Delete")
            
            # Cancel linked Sales Invoices
            try:
                sales_invoices = frappe.get_all("Sales Invoice", filters={"maintenance_order": doc.name, "docstatus": 1})
                for si_info in sales_invoices:
                    try:
                        si = frappe.get_doc("Sales Invoice", si_info.name)
                        si.flags.ignore_links = True
                        si.cancel()
                    except Exception as e:
                        frappe.log_error(f"Error canceling Sales Invoice {si_info.name} during cascade delete: {str(e)}", "Cascade Delete")
            except Exception as e:
                frappe.log_error(f"Error fetching Sales Invoices linked to {doc.name}: {str(e)}", "Cascade Delete")
        
        elif doc.doctype == "Maintenance Directing":
            for dt in ["External Processing", "Internal Processing"]:
                try:
                    links = frappe.get_all(dt, filters={"maintenance_directing": doc.name, "docstatus": 1})
                    for link in links:
                        try:
                            target = frappe.get_doc(dt, link.name)
                            target.flags.ignore_links = True
                            target.cancel()
                        except Exception as e:
                            frappe.log_error(f"Error canceling {dt} {link.name} during cascade delete: {str(e)}", "Cascade Delete")
                except Exception as e:
                    frappe.log_error(f"Error fetching {dt} linked to {doc.name}: {str(e)}", "Cascade Delete")
        
        elif doc.doctype == "Sales Order":
            try:
                mos = frappe.get_all("Maintenance Order", filters={"sales_order": doc.name, "docstatus": 1})
                for mo_info in mos:
                    try:
                        mo = frappe.get_doc("Maintenance Order", mo_info.name)
                        mo.flags.ignore_links = True
                        mo.cancel()
                    except Exception as e:
                        frappe.log_error(f"Error canceling Maintenance Order {mo_info.name} during cascade delete: {str(e)}", "Cascade Delete")
            except Exception as e:
                frappe.log_error(f"Error fetching Maintenance Orders linked to {doc.name}: {str(e)}", "Cascade Delete")
            
            try:
                sis = frappe.get_all("Sales Invoice", filters={"sales_order": doc.name, "docstatus": 1})
                for si_info in sis:
                    try:
                        si = frappe.get_doc("Sales Invoice", si_info.name)
                        si.flags.ignore_links = True
                        si.cancel()
                    except Exception as e:
                        frappe.log_error(f"Error canceling Sales Invoice {si_info.name} during cascade delete: {str(e)}", "Cascade Delete")
            except Exception as e:
                frappe.log_error(f"Error fetching Sales Invoices linked to {doc.name}: {str(e)}", "Cascade Delete")
        
        # Step 2: Delete all linked documents (now that they're cancelled or draft)
        if doc.doctype == "Maintenance Order":
            for dt in ["Maintenance Directing", "Maintenance Invoice", "External Processing", "Internal Processing", "Maintenance Payment"]:
                try:
                    links = frappe.get_all(dt, filters={"maintenance_order": doc.name})
                    for link in links:
                        try:
                            # Unlink before deletion to avoid reference errors
                            frappe.db.set_value(dt, link.name, "maintenance_order", None, update_modified=False)
                            frappe.delete_doc(dt, link.name, ignore_permissions=True, ignore_links=True)
                        except Exception as e:
                            frappe.log_error(f"Error deleting {dt} {link.name}: {str(e)}", "Cascade Delete")
                except Exception as e:
                    frappe.log_error(f"Error fetching {dt} linked to {doc.name}: {str(e)}", "Cascade Delete")
            
            # Delete linked Sales Order
            try:
                sales_order = doc.get("sales_order")
                if sales_order and frappe.db.exists("Sales Order", sales_order):
                    frappe.db.set_value("Sales Order", sales_order, "maintenance_order", None, update_modified=False)
                    frappe.delete_doc("Sales Order", sales_order, ignore_permissions=True, ignore_links=True)
            except Exception as e:
                frappe.log_error(f"Error deleting Sales Order: {str(e)}", "Cascade Delete")
            
            # Delete linked Sales Invoices
            try:
                sales_invoices = frappe.get_all("Sales Invoice", filters={"maintenance_order": doc.name})
                for si_info in sales_invoices:
                    try:
                        frappe.db.set_value("Sales Invoice", si_info.name, "maintenance_order", None, update_modified=False)
                        frappe.delete_doc("Sales Invoice", si_info.name, ignore_permissions=True, ignore_links=True)
                    except Exception as e:
                        frappe.log_error(f"Error deleting Sales Invoice {si_info.name}: {str(e)}", "Cascade Delete")
            except Exception as e:
                frappe.log_error(f"Error fetching Sales Invoices linked to {doc.name}: {str(e)}", "Cascade Delete")
        
        elif doc.doctype == "Maintenance Directing":
            for dt in ["External Processing", "Internal Processing"]:
                try:
                    links = frappe.get_all(dt, filters={"maintenance_directing": doc.name})
                    for link in links:
                        try:
                            frappe.db.set_value(dt, link.name, "maintenance_directing", None, update_modified=False)
                            frappe.delete_doc(dt, link.name, ignore_permissions=True, ignore_links=True)
                        except Exception as e:
                            frappe.log_error(f"Error deleting {dt} {link.name}: {str(e)}", "Cascade Delete")
                except Exception as e:
                    frappe.log_error(f"Error fetching {dt} linked to {doc.name}: {str(e)}", "Cascade Delete")
        
        elif doc.doctype == "Sales Order":
            try:
                mos = frappe.get_all("Maintenance Order", filters={"sales_order": doc.name})
                for mo_info in mos:
                    try:
                        frappe.db.set_value("Maintenance Order", mo_info.name, "sales_order", None, update_modified=False)
                        frappe.delete_doc("Maintenance Order", mo_info.name, ignore_permissions=True, ignore_links=True)
                    except Exception as e:
                        frappe.log_error(f"Error deleting Maintenance Order {mo_info.name}: {str(e)}", "Cascade Delete")
            except Exception as e:
                frappe.log_error(f"Error fetching Maintenance Orders linked to {doc.name}: {str(e)}", "Cascade Delete")
            
            try:
                sis = frappe.get_all("Sales Invoice", filters={"sales_order": doc.name})
                for si_info in sis:
                    try:
                        frappe.db.set_value("Sales Invoice", si_info.name, "sales_order", None, update_modified=False)
                        frappe.delete_doc("Sales Invoice", si_info.name, ignore_permissions=True, ignore_links=True)
                    except Exception as e:
                        frappe.log_error(f"Error deleting Sales Invoice {si_info.name}: {str(e)}", "Cascade Delete")
            except Exception as e:
                frappe.log_error(f"Error fetching Sales Invoices linked to {doc.name}: {str(e)}", "Cascade Delete")

    finally:
        frappe.local.maintenance_sync_processing.remove(doc_id)

