import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import nowdate

class TechnicianCustody(Document):
    def validate(self):
        self.validate_original_warehouse()
        self.set_custody_warehouse()

    def validate_original_warehouse(self):
        if not self.original_warehouse:
            frappe.throw(_("Please select Original Warehouse"))

    def set_custody_warehouse(self):
        if not self.custody_warehouse:
            # We will create/set the technician-specific warehouse upon submission or issuance logic.
            # For now, we'll try to find if a "Custody" warehouse for this employee exists.
            warehouse_name = f"Custody - {self.employee}"
            if frappe.db.exists("Warehouse", warehouse_name):
                self.custody_warehouse = warehouse_name

    def on_submit(self):
        self.create_issuance_stock_entry()
        self.update_maintenance_order_custody_status()

    def on_cancel(self):
        self.update_maintenance_order_custody_status()

    def update_maintenance_order_custody_status(self):
        # Determine overall custody status for the maintenance order
        all_custodies = frappe.get_all("Technician Custody", 
                                       filters={"maintenance_order": self.maintenance_order, "docstatus": 1},
                                       fields=["status"])
        
        if not all_custodies:
            overall_status = "No Custody"
        else:
            statuses = [c.status for c in all_custodies]
            if all(s == "Fully Returned" for s in statuses):
                overall_status = "Fully Returned"
            elif any(s in ["Issued", "Partially Returned"] for s in statuses):
                overall_status = "Partially Returned"
            else:
                overall_status = "No Custody" # Default
            
            # Special case for first one
            if len(all_custodies) == 1 and all_custodies[0].status == "Issued":
                overall_status = "Issued"

        frappe.db.set_value("Maintenance Order", self.maintenance_order, "custody_status", overall_status)

    def create_issuance_stock_entry(self):
        if self.stock_entry:
            return

        # Ensure technician warehouse exists
        self.ensure_custody_warehouse()

        se = frappe.get_doc({
            "doctype": "Stock Entry",
            "stock_entry_type": "Material Transfer",
            "company": frappe.db.get_value("Maintenance Order", self.maintenance_order, "company") or frappe.defaults.get_global_default("company"),
            "posting_date": nowdate(),
            "items": []
        })

        for item in self.items:
            se.append("items", {
                "item_code": item.item_code,
                "qty": item.qty_issued,
                "s_warehouse": self.original_warehouse,
                "t_warehouse": self.custody_warehouse,
                "basic_rate": frappe.db.get_value("Item", item.item_code, "valuation_rate") or 0
            })

        se.insert()
        se.submit()
        self.db_set("stock_entry", se.name)
        self.db_set("status", "Issued")

    def ensure_custody_warehouse(self):
        company = frappe.db.get_value("Maintenance Order", self.maintenance_order, "company") or frappe.defaults.get_global_default("company")
        warehouse_name = f"Custody - {self.employee}"
        
        # Check if the specific technician warehouse exists (any company)
        existing_w = frappe.db.get_value("Warehouse", {"warehouse_name": warehouse_name}, "name")
        if not existing_w:
            # Look for or create "Technician Custodies" group
            group_name = frappe.db.get_value("Warehouse", {"warehouse_name": "Technician Custodies", "is_group": 1}, "name")
            
            if not group_name:
                # Find any fallback group if we can't create one easily, but let's just create it under the root company
                group_doc = frappe.get_doc({
                    "doctype": "Warehouse",
                    "warehouse_name": "Technician Custodies",
                    "is_group": 1,
                    "company": company
                })
                group_doc.insert(ignore_permissions=True)
                parent_warehouse = group_doc.name
            else:
                parent_warehouse = group_name

            w_doc = frappe.get_doc({
                "doctype": "Warehouse",
                "warehouse_name": warehouse_name,
                "parent_warehouse": parent_warehouse,
                "company": company
            })
            w_doc.insert(ignore_permissions=True)
            self.custody_warehouse = w_doc.name
            self.db_set("custody_warehouse", w_doc.name)
        else:
            self.custody_warehouse = existing_w
            self.db_set("custody_warehouse", existing_w)

    @frappe.whitelist()
    def create_return_stock_entry(self, return_items):
        """Creates return stock entries and updates custody status."""
        if isinstance(return_items, str):
            return_items = frappe.parse_json(return_items)

        company = frappe.db.get_value("Maintenance Order", self.maintenance_order, "company") or frappe.defaults.get_global_default("company")
        
        # Organize items by return type to minimize Stock Entries
        movements = {
            "Transfer Back": [], # Working, Surplus
            "Damaged": [],       # Damaged
            "Issue": []          # Consumed
        }

        for r_item in return_items:
            qty = float(r_item.get("qty_returned_now") or 0)
            if qty <= 0:
                continue
            
            item_code = r_item.get("item_code")
            condition = r_item.get("return_condition")
            
            # Find the original child doc to update
            child_found = False
            for item in self.items:
                if item.item_code == item_code:
                    if (item.qty_returned or 0) + qty > item.qty_issued:
                        frappe.throw(_("Return quantity for {0} exceeds issued quantity").format(item_code))
                    
                    item.qty_returned = (item.qty_returned or 0) + qty
                    child_found = True
                    break
            
            if not child_found:
                continue

            entry_item = {
                "item_code": item_code,
                "qty": qty,
                "s_warehouse": self.custody_warehouse,
                "basic_rate": frappe.db.get_value("Item", item_code, "valuation_rate") or 0
            }

            if condition in ["Working", "Surplus"]:
                entry_item["t_warehouse"] = self.original_warehouse
                movements["Transfer Back"].append(entry_item)
            elif condition == "Damaged":
                # Ensure Damaged Warehouse exists
                damaged_warehouse = self.ensure_damaged_warehouse()
                entry_item["t_warehouse"] = damaged_warehouse
                movements["Damaged"].append(entry_item)
            elif condition == "Consumed":
                movements["Issue"].append(entry_item)

        # Create Stock Entries
        for entry_type, items in movements.items():
            if not items:
                continue
            
            se_type = "Material Transfer" if entry_type != "Issue" else "Material Issue"
            se = frappe.get_doc({
                "doctype": "Stock Entry",
                "stock_entry_type": se_type,
                "company": company,
                "posting_date": nowdate(),
                "items": items,
                "remarks": f"Return from Custody {self.name}"
            })
            se.insert()
            se.submit()
            # We can store the last return stock entry or just log it
            self.db_set("return_stock_entry", se.name)

        # Update Overall Status
        self.update_status()
        self.save()
        self.update_maintenance_order_custody_status()

    def update_status(self):
        all_returned = True
        any_returned = False
        for item in self.items:
            if (item.qty_returned or 0) < item.qty_issued:
                all_returned = False
            if (item.qty_returned or 0) > 0:
                any_returned = True
        
        if all_returned:
            self.status = "Fully Returned"
        elif any_returned:
            self.status = "Partially Returned"
        else:
            self.status = "Issued"

    def ensure_damaged_warehouse(self):
        damaged_name = "Damaged Goods - Technician Custody"
        company = frappe.db.get_value("Maintenance Order", self.maintenance_order, "company") or frappe.defaults.get_global_default("company")
        
        existing_w = frappe.db.get_value("Warehouse", {"warehouse_name": damaged_name, "company": company}, "name")
        if not existing_w:
            w_doc = frappe.get_doc({
                "doctype": "Warehouse",
                "warehouse_name": damaged_name,
                "company": company
            })
            w_doc.insert(ignore_permissions=True)
            return w_doc.name
        return existing_w

    @frappe.whitelist()
    def return_items(self):
        pass
