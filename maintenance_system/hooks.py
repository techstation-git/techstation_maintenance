app_name = 'maintenance_system'
app_title = 'maintenance_system'
app_description = 'maintenance_system description'
app_version = '0.0.1'

# Fixtures to export/import with bench migrate
fixtures = [
    {
        "dt": "Custom HTML Block",
        "filters": [["name", "in", ["Maintenance Operation Dashboard", "Maintenance Operations Dashboard"]]]
    },
    {
        "dt": "Property Setter",
        "filters": [["doc_type", "=", "Sales Order"], ["field_name", "=", "order_type"], ["property", "in", ["default", "reqd", "hidden"]]]
    }
]

# Document event hooks for notifications
doc_events = {
    "Maintenance Order": {
        "on_submit": "maintenance_system.maintenance_system.notifications.on_maintenance_order_submit",
        "on_update_after_submit": "maintenance_system.maintenance_system.notifications.on_maintenance_order_update",
        "on_cancel": "maintenance_system.maintenance_system.sync.cascade_cancel",
        "on_trash": "maintenance_system.maintenance_system.sync.cascade_delete",
    },
    "Maintenance Directing": {
        "on_cancel": "maintenance_system.maintenance_system.sync.cascade_cancel",
        "on_trash": "maintenance_system.maintenance_system.sync.cascade_delete",
    },
    "External Processing": {
        "on_cancel": "maintenance_system.maintenance_system.sync.cascade_cancel",
        "on_trash": "maintenance_system.maintenance_system.sync.cascade_delete",
    },
    "Internal Processing": {
        "on_cancel": "maintenance_system.maintenance_system.sync.cascade_cancel",
        "on_trash": "maintenance_system.maintenance_system.sync.cascade_delete",
    },
    "Maintenance Invoice": {
        "on_cancel": "maintenance_system.maintenance_system.sync.cascade_cancel",
        "on_trash": "maintenance_system.maintenance_system.sync.cascade_delete",
    },
    "Maintenance Payment": {
        "on_cancel": "maintenance_system.maintenance_system.sync.cascade_cancel",
        "on_trash": "maintenance_system.maintenance_system.sync.cascade_delete",
    },
    "Sales Order": {
        "on_cancel": "maintenance_system.maintenance_system.sync.cascade_cancel",
        "on_trash": "maintenance_system.maintenance_system.sync.cascade_delete",
    }
}

permission_query_conditions = {
    "Maintenance Order": "maintenance_system.maintenance_system.doctype.maintenance_order.maintenance_order.get_permission_query_conditions"
}

# Scheduled tasks
scheduler_events = {
    "hourly": [
        "maintenance_system.tasks.check_overdue_tickets",
    ]
}
