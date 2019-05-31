# -*- coding: utf-8 -*-
{
    'name': 'Innograph - Synchronization with LKPP',
    'version': '10.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Port Cities Ltd',
    'website': 'https://www.portcities.net',
    'category': 'Sales',
    'summary': 'LKPP Connector.',
    'depends': ['website_sale'],
    'data': [
        'data/ir_config_parameter.xml',
        'data/ir_cron.xml',
        'views/res_config_views.xml',
        'views/product_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False
}
