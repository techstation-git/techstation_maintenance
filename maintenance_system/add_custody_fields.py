#!/usr/bin/env python3
"""
Add Custody Custom Fields to Maintenance Order
Phase 2: Custody Management System

This script adds the following custom fields:
1. custody_issued - Checkbox to track if custody has been issued
2. custody_returned - Checkbox to track if custody has been returned
3. custody_status - Select field for custody status
4. linked_custody - Link to Technician Custody record

Usage:
    bench --site [site-name] execute maintenance_system.add_custody_fields.execute
"""

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
    """Add custody custom fields to Maintenance Order"""
    
    custom_fields = {
        "Maintenance Order": [
            {
                "fieldname": "custody_section",
                "label": "Custody Management",
                "fieldtype": "Section Break",
                "insert_after": "table_66",
                "collapsible": 1,
                "description": "Track materials and tools issued to technicians"
            },
            {
                "fieldname": "custody_issued",
                "label": "Custody Issued",
                "fieldtype": "Check",
                "insert_after": "custody_section",
                "read_only": 1,
                "default": "0",
                "description": "Materials/tools have been issued to technician"
            },
            {
                "fieldname": "custody_returned",
                "label": "Custody Returned",
                "fieldtype": "Check",
                "insert_after": "custody_issued",
                "read_only": 1,
                "default": "0",
                "description": "All custody items have been returned"
            },
            {
                "fieldname": "column_break_custody",
                "fieldtype": "Column Break",
                "insert_after": "custody_returned"
            },
            {
                "fieldname": "custody_status",
                "label": "Custody Status",
                "fieldtype": "Select",
                "insert_after": "column_break_custody",
                "options": "Not Issued\nIssued\nPartially Returned\nFully Returned\nOverdue",
                "default": "Not Issued",
                "read_only": 1,
                "in_list_view": 0,
                "in_standard_filter": 1,
                "description": "Current status of custody items"
            },
            {
                "fieldname": "linked_custody",
                "label": "Custody Record",
                "fieldtype": "Link",
                "insert_after": "custody_status",
                "options": "Technician Custody",
                "read_only": 1,
                "show_in_connections": 1,
                "description": "Linked Technician Custody record"
            }
        ]
    }
    
    print("Creating custody custom fields for Maintenance Order...")
    create_custom_fields(custom_fields, update=True)
    
    print("✅ Custody custom fields created successfully!")
    print("\nFields added:")
    print("  1. Custody Section (Section Break)")
    print("  2. Custody Issued (Check)")
    print("  3. Custody Returned (Check)")
    print("  4. Custody Status (Select)")
    print("  5. Linked Custody (Link to Technician Custody)")
    print("\nNext steps:")
    print("  - Clear cache: bench --site [site-name] clear-cache")
    print("  - Refresh browser")
    print("  - Open Maintenance Order to see new custody section")


if __name__ == "__main__":
    execute()
