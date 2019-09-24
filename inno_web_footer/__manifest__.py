# -*- coding: utf-8 -*-
{
    'name': 'Innograph Custom Website Footer',
    'version': '10.0.1.0',
    "author": "Port Cities",
    'category': 'eCommerce',
    'summary': 'Customizing eCommerce website footer',
    'description': """
        *Author : SWS <satrio@portcities.net>
    """,
    'depends': [
        'website_sale',
        'website',
        'website_mass_mailing',
        'theme_stoneware',
    ],
    'data': [
        'views/templates.xml',
        'views/website_views.xml',
        'views/res_config_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False
}
