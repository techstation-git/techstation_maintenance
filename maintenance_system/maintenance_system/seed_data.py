import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_field

def run():
    # 1. Custom Field
    try:
        if not frappe.get_meta('Employee').has_field('technician_type'):
            create_custom_field('Employee', {
                'fieldname': 'technician_type',
                'label': 'Technician Type',
                'fieldtype': 'Select',
                'options': '\nTechnician\nAssistant',
                'insert_after': 'designation'
            })
            print("Custom field created")
    except Exception as e:
        print(f"Error creating custom field: {e}")

    # 2. Ticket Types
    try:
        types = ['Implementation', 'Maintenance', 'Service', 'Repair', 'Installation', 'Field Repair']
        for t_name in types:
            if not frappe.db.exists('Maintenance Ticket Type', t_name):
                frappe.get_doc({
                    'doctype': 'Maintenance Ticket Type',
                    'ticket_type_name': t_name,
                    'is_default': 1 if t_name == 'Field Repair' else 0
                }).insert()
                print(f"Ticket Type {t_name} created")
    except Exception as e:
        print(f"Error creating ticket types: {e}")

    # 3. Roles
    try:
        for role in ['Technician', 'Assistant']:
            if not frappe.db.exists('Role', role):
                frappe.get_doc({'doctype': 'Role', 'role_name': role}).insert()
                print(f"Role {role} created")
    except Exception as e:
        print(f"Error creating roles: {e}")

    # 4. Mock Employee
    try:
        if frappe.db.exists('Employee', 'HR-EMP-00001'):
            frappe.db.set_value('Employee', 'HR-EMP-00001', 'technician_type', 'Technician')
            print("Employee updated")
    except Exception as e:
        print(f"Error updating employee: {e}")

    frappe.db.commit()

if __name__ == "__main__":
    run()
