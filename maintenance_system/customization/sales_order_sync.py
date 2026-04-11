import frappe

def on_cancel(doc, method):
    if frappe.flags.in_maintenance_order_sync:
        return

    # Find Maintenance Orders linked to this Sales Order
    mos = frappe.get_all("Maintenance Order", filters={"sales_order": doc.name, "docstatus": 1})
    if not mos:
        return

    frappe.flags.in_maintenance_order_sync = True
    for mo_info in mos:
        mo = frappe.get_doc("Maintenance Order", mo_info.name)
        mo.cancel()
    frappe.flags.in_maintenance_order_sync = False

def on_trash(doc, method):
    if frappe.flags.in_maintenance_order_sync:
        return

    # Find Maintenance Orders linked to this Sales Order
    # They should be cancelled (docstatus 2) to be deleted
    mos = frappe.get_all("Maintenance Order", filters={"sales_order": doc.name, "docstatus": 2})
    if not mos:
        return

    frappe.flags.in_maintenance_order_sync = True
    for mo_info in mos:
        mo = frappe.get_doc("Maintenance Order", mo_info.name)
        mo.delete()
    frappe.flags.in_maintenance_order_sync = False
