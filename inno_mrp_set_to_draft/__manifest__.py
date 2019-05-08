# -*- coding: utf-8 -*-
{
    'name': 'Innograph - Custom Manufacturing Order',
    'version': '10.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Port Cities Ltd',
    'website': 'https://www.portcities.net',
    'category': 'Manufacturing',
    'summary': 'Custom Manufacturing Order.',
    'depends': ['mrp_production_draft'],
    'data': [
        'views/mrp_production_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False
}
