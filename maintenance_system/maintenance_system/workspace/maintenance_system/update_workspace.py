
import json
import os

def update_workspace():
    filepath = "/home/abeddy/techstation/apps/maintenance_system/maintenance_system/maintenance_system/workspace/maintenance_system/maintenance_system.json"
    
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    # Update link_count for "Follow Up" card
    for link in data.get("links", []):
        if link.get("label") == "Follow Up" and link.get("type") == "Card Break":
            link["link_count"] = 2
            break
            
    # Add the new report link if it doesn't exist
    report_label = "Labor Capacity View Report"
    exists = any(link.get("label") == report_label for link in data.get("links", []))
    
    if not exists:
        new_link = {
            "hidden": 0,
            "is_query_report": 1,
            "label": report_label,
            "link_count": 0,
            "link_to": report_label,
            "link_type": "Report",
            "onboard": 0,
            "type": "Link"
        }
        # Insert after "Customer Feedback" or at the end of the links
        data["links"].append(new_link)
        print(f"Added {report_label} to workspace links.")
    else:
        print(f"{report_label} already exists in workspace links.")
        
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=1)
    
    print("Workspace updated successfully.")

if __name__ == "__main__":
    update_workspace()
