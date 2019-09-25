# -*- coding: utf-8 -*-
{
    'name': 'Innograph Website Product Details',
    'version': '10.0.1.0',
    "author": "Port Cities",
    'category': 'eCommerce',
    'summary': 'Customizing eCommerce Product',
    'description': """
        *Author : Saiful Rijal
    """,
    'depends': [
        'theme_stoneware', 
        'product',
    ],
    'data': [
        'views/templates.xml', 
        'views/website.xml', 
    ],
    'installable': True,
    'application': True,
    'auto_install': False
}
