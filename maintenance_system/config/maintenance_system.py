from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
                        "label": _("Operations"),
                        "items": [
				{
                                        "type": "doctype",
                                        "name": "Maintenance Item",
                                        "label": "Maintenance Item",
                                        "description": _("Maintenance Item"),
                                        "onboard": 1
                                },
				{
                                        "type": "doctype",
                                        "name": "Receive Maintenance Item",
                                        "label": "Receive Maintenance Item",
                                        "description": _("Receive Maintenance Item"),
                                        "onboard": 1
                                },
                                {
                                        "type": "doctype",
                                        "name": "Maintenance Order",
                                        "label": "Maintenance Order",
                                        "description": _("Maintenance Order"),
                                        "onboard": 1
                                },
				{
                                        "type": "doctype",
                                        "name": "Maintenance Directing",
                                        "label": "Maintenance Directing",
                                        "description": _("Maintenance Directing"),
                                        "onboard": 1
                                },
				{
                                        "type": "doctype",
                                        "name": "Maintenance Invoice",
                                        "label": "Maintenance Invoice",
                                        "description": _("Maintenance Invoice"),
                                        "onboard": 1
                                }
                        ]
                },
		{
                        "label": _("Maintenance"),
                        "items": [
                                {
                                        "type": "doctype",
                                        "name": "Internal Processing",
                                        "label": "Internal Processing",
                                        "description": _("Internal Processing"),
                                        "onboard": 1
                                },
				{
                                        "type": "doctype",
                                        "name": "External Processing",
                                        "label": "External Processing",
                                        "description": _("External Processing"),
                                        "onboard": 1
                                },
				{
                                        "type": "doctype",
                                        "name": "Maintenance Feedback",
                                        "label": "Maintenance Feedback",
                                        "description": _("Maintenance Feedback"),
                                        "onboard": 1
                                }
                        ]
                },
		{
                        "label": _("Payment"),
                        "items": [
                                {
                                        "type": "doctype",
                                        "name": "Maintenance Payment",
                                        "label": "Maintenance Payment",
                                        "description": _("Maintenance Payment"),
                                        "onboard": 1
                                }
                        ]
                },
		{
                        "label": _("Warehouse"),
                        "items": [
                                {
                                        "type": "doctype",
                                        "name": "Maintenance Material Receipt",
                                        "label": "Maintenance Material Receipt",
                                        "description": _("Maintenance Material Receipt"),
                                        "onboard": 1
                                }
                        ]
                },
		{
                        "label": _("Module Setup"),
                        "items": [
				{
                                        "type": "doctype",
                                        "name": "Maintenance Department",
                                        "label": "Maintenance Department",
                                        "description": _("Maintenance Department"),
                                        "onboard": 1
                                },
				{
                                        "type": "doctype",
                                        "name": "Maintenance Team",
                                        "label": "Maintenance Team",
                                        "description": _("Maintenance Team"),
                                        "onboard": 1
                                },
				{
                                        "type": "doctype",
                                        "name": "Maintenance Support Car",
                                        "label": "Maintenance Support Car",
                                        "description": _("Maintenance Support Car"),
                                        "onboard": 1
                                },
				{
                                        "type": "doctype",
                                        "name": "Maintenance Categorie",
                                        "label": "Maintenance Categorie",
                                        "description": _("Maintenance Categorie"),
                                        "onboard": 1
                                },
				{
                                        "type": "doctype",
                                        "name": "Maintenance Service",
                                        "label": "Maintenance Service",
                                        "description": _("Maintenance Service"),
                                        "onboard": 1
                                },
				{
                                        "type": "doctype",
                                        "name": "Maintenance Malfunction",
                                        "label": "Maintenance Malfunction",
                                        "description": _("Maintenance Malfunction"),
                                        "onboard": 1
                                },
				{
                                        "type": "doctype",
                                        "name": "Maintenance Schedule List",
                                        "label": "Maintenance Schedule",
                                        "description": _("Maintenance Schedule List"),
                                        "onboard": 1
                                },
                                {
                                        "type": "doctype",
                                        "name": "Warranty Template",
                                        "label": "Warranty Template",
                                        "description": _("Warranty Template"),
                                        "onboard": 1
                                }
                        ]
                },
		{
                        "label": _("Settings"),
                        "items": [
                                {
                                        "type": "doctype",
                                        "name": "Maintenance System Settings",
                                        "label": "Maintenance System Settings",
                                        "description": _("Maintenance System Settings"),
                                        "onboard": 1
                                },
				{
                                        "type": "doctype",
                                        "name": "Maintenance Payment Methods",
                                        "label": "Maintenance Payment Methods",
                                        "description": _("Maintenance Payment Methods"),
                                        "onboard": 1
                                }
                        ]
                },
		{
                        "label": _("Reports"),
                        "items": [
                                {
		                        "type": "report",
                		        "is_query_report": True,
                		        "name": "Maintenance Received Item Summery",
                        		"doctype": "Receive Maintenance Item"
                		},
				{
                                        "type": "report",
                                        "is_query_report": True,
                                        "name": "Maintenance Revenue Collection",
                                        "doctype": "Maintenance Invoice"
                                },
				{
                                        "type": "report",
                                        "is_query_report": True,
                                        "name": "Maintenance Assignment",
                                        "doctype": "Maintenance Directing"
                                },
				{
                                        "type": "report",
                                        "is_query_report": True,
                                        "name": "Department Wise Maintenance Tracking",
                                        "doctype": "Maintenance Directing"
                                },
				{
                                        "type": "report",
                                        "is_query_report": True,
                                        "name": "Maintenance Feedback Review",
                                        "doctype": "Maintenance Invoice"
                                }
                        ]
                }
]
