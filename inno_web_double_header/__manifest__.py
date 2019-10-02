# -*- coding: utf-8 -*-
{
    'name': 'Innograph Fix double header',
    'version': '10.0.1.0.0',
    'license': 'AGPL-3',
    "author": "Port Cities",
    'category': 'eCommerce',
    'summary': 'Fix double header',
    'contributors': [
        'Alfif Nurmirza Maulana',
    ],
    'description': """
        Fix double header
    """,
    'depends': [
        'website_sale','inno_web_header',
        'web'],
    'data': [                                                         
        'views/imp_header.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': False
}

