# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "maintenance_system"
app_title = "Maintenance System"
app_publisher = "Tech Station"
app_description = "Complete Maintenance System with Cascading Sync and Rewards"
app_icon = "octicon octicon-tools"
app_color = "grey"
app_email = "developer@techstation.com"
app_license = "MIT"

# Document UI overrides
doctype_js = {
    "Sales Order": "public/js/sales_order.js",
    "Delivery Note": "public/js/delivery_note.js",
    "Sales Invoice": "public/js/sales_invoice.js",
    "Item": "public/js/item.js",
    "Customer": "public/js/customer.js"
}

# Fixtures to export/import with bench migrate
# -------------------------------------------
fixtures = [
    # UI Components
    {
        "dt": "Custom HTML Block",
        "filters": [["name", "in", ["Maintenance Operation Dashboard", "Maintenance Operations Dashboard"]]]
    },
    # Property Setters
    {
        "doctype": "Property Setter",
        "filters": [
            ["doc_type", "=", "Sales Order"], 
            ["field_name", "=", "order_type"], 
            ["property", "in", ["default", "reqd", "hidden"]]
        ]
    },
    {
        "doctype": "Property Setter",
        "filters": [["name", "=", "Item-warranty_period-hidden"]]
    },
    # Custom Schemas
    {"dt": "DocType", "filters": [["name", "in", ["Maintenance Schedule List", "Technician Custody", "Custody Item"]]]},
    {"dt": "Client Script", "filters": [["dt", "in", ["Warranty Template", "Maintenance Item", "Sales Invoice", "Maintenance Schedule List", "Maintenance Team"]]]},
    {
        "doctype": "Custom Field",
        "filters": [["name", "in", [
            "Item-warranty_template", "Item-warranty_status", "Item-maintenance_categories",
            "Sales Order Item-warranty_template", "Sales Order Item-warranty_status",
            "Delivery Note Item-warranty_template", "Delivery Note Item-warranty_status",
            "Sales Invoice Item-warranty_template", "Sales Invoice-warranty_created",
            "Sales Invoice Item-warranty_status", "Sales Invoice Item-warranty_created",
            "Payment Entry-allocated_in_maintenance", "Stock Entry-maintenance_products_receipt",
            "GL Entry-unallocated", "Mode of Payment-show_in_maintenance_for_payment",
            "Customer-mobile", "Branch-enable", "Branch-default_branch", "Employee-specializations"
        ]]]
    },
    # Permissions and Roles
    {
        "doctype": "Role",
        "filters": [["name", "in", [
            "Maintenance Item", "Maintenance User", "Maintenance Directing", "Maintenance Invoice",
            "Maintenance Order", "Maintenance Manager", "Maintenance Internal", "Maintenance External",
            "Maintenance Payment", "Maintenance Commission", "Maintenance Material", "Maintenance Supervisor",
            "Operations Officer"
        ]]]
    },
    {
        "doctype": "Custom DocPerm",
        "filters": [["parent", "in", [
            'Address','POS Profile','Item Status','Commission Payment','Item Price',
            'Maintenance Schedule List','Maintenance Malfunction','Tax Category',
            'Maintenance Service','Maintenance Invoice','Maintenance Item','Territory',
            'Maintenance Department','Warehouse','Internal Processing','User',
            'Maintenance Categorie','Maintenance Schedule','Warranty Template',
            'Maintenance Team','Maintenance System Settings','External Processing',
            'Item Color','Contact','Maintenance Material Receipt',
            'Sales Taxes and Charges Template','Branch','Pick List','Item Model','Maintenance Order',
            'User Permission','Customer','Web Template','Cost Center','Price List',
            'Maintenance Material Request','Employee Specialization', 'Technician Custody','Custody Item'
        ]]]
    },
    {"dt": "Module Profile", "filters": [["name", "=", "Maintenance System"]]},
    "Workflow", "Workflow State"
]

# Document Events
# ---------------
doc_events = {
    # Validations from Live
    "Maintenance Item": {
        "on_update_after_submit": "maintenance_system.maintenance_system.doctype.maintenance_item.maintenance_item.on_update_data_self"
    },
    "Customer": {
        "validate": "maintenance_system.customization.customer.on_update_mobile"
    },
    # Main Workflow with Cascading Sync (Apps) and Notifications (Both)
    "Maintenance Order": {
        # Notifications
        "after_insert": "maintenance_system.maintenance_system.doctype.maintenance_order.maintenance_order.notify_sales_person_on_create",
        "on_submit": "maintenance_system.maintenance_system.notifications.on_maintenance_order_submit",
        "on_update": "maintenance_system.maintenance_system.doctype.maintenance_order.maintenance_order.notify_sales_person_on_update",
        "on_update_after_submit": "maintenance_system.maintenance_system.notifications.on_maintenance_order_update",
        # Cascade Sync
        "on_cancel": "maintenance_system.maintenance_system.sync.cascade_cancel",
        "on_trash": "maintenance_system.maintenance_system.sync.cascade_delete"
    },
    "Sales Order": {
        "on_cancel": "maintenance_system.maintenance_system.sync.cascade_cancel",
        "on_trash": "maintenance_system.maintenance_system.sync.cascade_delete"
    },
    "Maintenance Directing": {
        "on_cancel": "maintenance_system.maintenance_system.sync.cascade_cancel",
        "on_trash": "maintenance_system.maintenance_system.sync.cascade_delete"
    },
    "External Processing": {
        "on_cancel": "maintenance_system.maintenance_system.sync.cascade_cancel",
        "on_trash": "maintenance_system.maintenance_system.sync.cascade_delete"
    },
    "Internal Processing": {
        "on_cancel": "maintenance_system.maintenance_system.sync.cascade_cancel",
        "on_trash": "maintenance_system.maintenance_system.sync.cascade_delete"
    },
    "Maintenance Invoice": {
        "on_cancel": "maintenance_system.maintenance_system.sync.cascade_cancel",
        "on_trash": "maintenance_system.maintenance_system.sync.cascade_delete"
    },
    "Maintenance Payment": {
        "on_cancel": "maintenance_system.maintenance_system.sync.cascade_cancel",
        "on_trash": "maintenance_system.maintenance_system.sync.cascade_delete"
    }
}

# Overriding Methods
override_doctype_class = {
    "Sales Invoice": "maintenance_system.customization.sales_invoice.SalesInvoice"
}

# Permissions
permission_query_conditions = {
    "Maintenance Order": "maintenance_system.maintenance_system.doctype.maintenance_order.maintenance_order.get_permission_query_conditions"
}

# Scheduled Tasks
scheduler_events = {
    "hourly": [
        "maintenance_system.tasks.check_overdue_tickets",
    ]
}
