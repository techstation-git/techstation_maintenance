from __future__ import unicode_literals
import frappe
from frappe import _


def get_data():
	d = frappe.get_installed_apps()
	if "maintenance_system" in d:
		return {
			'heatmap': True,
			'heatmap_message': _('This is based on transactions against this Customer. See timeline below for details'),
			'fieldname': 'customer',
			'non_standard_fieldnames': {
				'Payment Entry': 'party',
				'Quotation': 'party_name',
				'Opportunity': 'party_name',
				'Maintenance Payment': 'party'
			},
			'dynamic_links': {
				'party_name': ['Customer', 'quotation_to']
			},
			'transactions': [
				{
					'label': _('Pre Sales'),
					'items': ['Opportunity', 'Quotation']
				},
				{
					'label': _('Orders'),
					'items': ['Sales Order', 'Delivery Note', 'Sales Invoice']
				},
				{
					'label': _('Payments'),
					'items': ['Payment Entry']
				},
				{
					'label': _('Support'),
					'items': ['Issue']
				},
				{
					'label': _('Projects'),
					'items': ['Project']
				},
				{
					'label': _('Pricing'),
					'items': ['Pricing Rule']
				},
				{
					'label': _('Subscriptions'),
					'items': ['Subscription']
				},
				{
       	                	        'label': _('Maintenance'),
               	                	'items': ['Maintenance Item','Receive Maintenance Item','Maintenance Order','Maintenance Processing','Maintenance Invoice','Maintenance Payment']
                       		}
			]
		}

	else:
		return {
		'heatmap': True,
		'heatmap_message': _('This is based on transactions against this Customer. See timeline below for details'),
		'fieldname': 'customer',
		'non_standard_fieldnames': {
			'Payment Entry': 'party',
			'Quotation': 'party_name',
			'Opportunity': 'party_name'
		},
		'dynamic_links': {
			'party_name': ['Customer', 'quotation_to']
		},
		'transactions': [
			{
				'label': _('Pre Sales'),
				'items': ['Opportunity', 'Quotation']
			},
			{
				'label': _('Orders'),
				'items': ['Sales Order', 'Delivery Note', 'Sales Invoice']
			},
			{
				'label': _('Payments'),
				'items': ['Payment Entry']
			},
			{
				'label': _('Support'),
				'items': ['Issue']
			},
			{
				'label': _('Projects'),
				'items': ['Project']
			},
			{
				'label': _('Pricing'),
				'items': ['Pricing Rule']
			},
			{
				'label': _('Subscriptions'),
				'items': ['Subscription']
			}
		]
	}
