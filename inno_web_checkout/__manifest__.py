# -*- coding: utf-8 -*-
{
    'name': 'Innograph Custom Checkout',
    'version': '10.0.1.0',
    "author": "Port Cities",
    'category': 'eCommerce',
    'summary': 'Customizing eCommerce website checkout',
    'description': """
        Customizing eCommerce website checkout
    """,
    'depends': [
        'theme_stoneware',
    ],
    'data': [
        'data/mail_template.xml',
        'views/website_sale_template.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False
}