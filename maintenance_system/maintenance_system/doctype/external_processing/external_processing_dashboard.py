from __future__ import unicode_literals
from frappe import _


def get_data():
    return {
        'heatmap': True,
        'fieldname': 'processing',
        'transactions': [
			{
                'label': _('Maintenance Material'),
                'items': [ "Maintenance Material Receipt"]
            },
			{
                'label': _('Fullfillment'),
                'items': [ "Maintenance Invoice"]
            }
        ]
    }
