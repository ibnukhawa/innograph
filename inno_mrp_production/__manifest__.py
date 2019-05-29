# -*- coding: utf-8 -*-
{
    'name': 'Innograph - Custom Manufacturing Order',
    'version': '10.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Port Cities Ltd',
    'website': 'https://www.portcities.net',
    'category': 'Manufacturing',
    'summary': 'Custom Manufacturing Order.',
    'depends': ['sale', 'mrp_production_draft', 'stock_mts_mto_rule'],
    'data': [
        'data/ir_sequence_data.xml',
        'security/ir.model.access.csv',
        'views/sale_order_view.xml',
        'views/mrp_production_view.xml',
        'views/mrp_bom_view.xml',
        'views/mrp_part_request_view.xml',
        'views/material_request_printout.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': False
}
