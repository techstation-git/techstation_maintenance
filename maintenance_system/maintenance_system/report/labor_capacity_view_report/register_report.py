
import frappe

def register_report():
    report_name = "Labor Capacity View Report"
    if not frappe.db.exists("Report", report_name):
        print(f"Creating Report record for {report_name}...")
        report = frappe.get_doc({
            "doctype": "Report",
            "report_name": report_name,
            "report_type": "Script Report",
            "ref_doctype": "Maintenance Order",
            "module": "Maintenance System",
            "is_standard": "Yes"
        })
        report.insert(ignore_permissions=True)
        frappe.db.commit()
        print("Report created successfully.")
    else:
        print(f"Report {report_name} already exists in database.")

if __name__ == "__main__":
    register_report()
