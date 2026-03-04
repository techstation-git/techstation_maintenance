app_name = 'maintenance_system'
app_title = 'maintenance_system'
app_description = 'maintenance_system description'
app_version = '0.0.1'

# Fixtures to export/import with bench migrate
fixtures = [
    {
        "dt": "Custom HTML Block",
        "filters": [["name", "=", "Maintenance Operations Dashboard"]]
    }
]

# Document event hooks for notifications
doc_events = {
    "Maintenance Order": {
        "on_submit": "maintenance_system.maintenance_system.notifications.on_maintenance_order_submit",
        "on_update_after_submit": "maintenance_system.maintenance_system.notifications.on_maintenance_order_update",
    }
}

# Scheduled tasks
scheduler_events = {
    "daily": [
        "maintenance_system.maintenance_system.notifications.send_72hr_overdue_alerts",
    ]
}
