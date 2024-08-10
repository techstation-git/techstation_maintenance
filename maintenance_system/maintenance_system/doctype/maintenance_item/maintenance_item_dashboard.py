from __future__ import unicode_literals
from frappe import _


def get_data():
    return {
        'heatmap': True,
        'fieldname': 'maintenance_item',
        'transactions': [
            {
                'label': _('Maintenance'),
                'items': ['Maintenance Order']
            },
			
        ]
    }