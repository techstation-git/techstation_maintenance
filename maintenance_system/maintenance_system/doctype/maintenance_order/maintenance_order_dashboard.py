from __future__ import unicode_literals
from frappe import _


def get_data():
    return {
        'heatmap': True,
        'fieldname': 'maintenance_order',
        'transactions': [
            {
                'label': _('Maintenance'),
                'items': ['Maintenance Directing']
            },
			{
                'label': _('Processing'),
                'items': [ "Internal Processing", "External Processing"]
            },
			{
                'label': _('Fullfillment'),
                'items': [ "Maintenance Invoice"]
            }
        ]
    }
