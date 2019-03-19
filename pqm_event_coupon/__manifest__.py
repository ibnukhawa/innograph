# -*- coding: utf-8 -*-
{
    'name': 'PQM Event Coupon',
    'version': '10.0.1.0.0',
    'author': 'Portcities Ltd',
    'website': 'http://www.portcities.net',
    'summary': "PQM Custom Event Coupon",
    'contributors': [
        'Dwiki Adnan F.',
        'Dhimas Yudangga A',
    ],
    'description': """
    - Coupon 
    """,
    'category': 'PQM PHASE 4',
    'depends': [
        'event', 
        'event_sale',
        'pqm_event_core',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/event_coupon_view.xml',
        'views/event_coupon_template.xml'
    ],
    'auto_install': False,
    'installable': True,
    'application': False,
}