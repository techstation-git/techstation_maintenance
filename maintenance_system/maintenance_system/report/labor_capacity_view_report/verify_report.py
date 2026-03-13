
import frappe
from maintenance_system.maintenance_system.report.labor_capacity_view_report.labor_capacity_view_report import execute

def test_report_logic():
    print("Testing Labor Capacity View Report Logic...")
    
    # Mock filters
    filters = {"company": "Tech Station"}
    
    try:
        columns, data = execute(filters)
        
        print(f"Columns: {[c['label'] for c in columns]}")
        print(f"Data Rows: {len(data)}")
        
        for row in data:
            print(f"Specialty: {row['specialty']}, Orders: {row['active_orders']}, Techs: {row['available_technicians']}, Gap: {row['capacity_gap']}")
            
            # Basic validation
            if row['capacity_gap'] != row['available_technicians'] - row['active_orders']:
                print(f"FAILED: Gap calculation incorrect for {row['specialty']}")
                return False
                
        print("Success: Report logic verification completed (Calculations only).")
        return True
    except Exception as e:
        print(f"Error during verification: {e}")
        return False

if __name__ == "__main__":
    # Note: This requires a frappe environment to run properly
    # For now, we will perform manual sanity check of the code
    pass
