#!/bin/bash
# Setup script for Phase 2: Custody Management System
# Run this script to set up the custody management features

SITE_NAME="techstation.com"

echo "🚀 Phase 2: Setting up Custody Management System..."
echo ""

# Step 1: Migrate database to create new doctypes
echo "Step 1/3: Creating database tables for Technician Custody..."
bench --site $SITE_NAME migrate
echo "✅ Database migration complete"
echo ""

# Step 2: Add custody custom fields to Maintenance Order
echo "Step 2/3: Adding custody fields to Maintenance Order..."
bench --site $SITE_NAME execute maintenance_system.add_custody_fields.execute
echo "✅ Custom fields added"
echo ""

# Step 3: Clear cache
echo "Step 3/3: Clearing cache..."
bench --site $SITE_NAME clear-cache
echo "✅ Cache cleared"
echo ""

echo "🎉 Custody Management System setup complete!"
echo ""
echo "Next steps:"
echo "  1. Refresh your browser"
echo "  2. Open a Maintenance Order (submitted)"
echo "  3. Click 'Issue Custody' button to test"
echo ""
echo "Files created:"
echo "  - Technician Custody DocType"
echo "  - Custody Item child table"
echo "  - Custom fields on Maintenance Order"
echo "  - UI buttons and dialogs"
