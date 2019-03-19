# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'PQM Custom Redirect Page',
    'author': 'Port Cities',
    'description': """
redirect to login page not homepage
after login, redirect to...\n
make default botton home \n
Author : Saiful Rijal\n

    """,
    'version': '1.0',
    'category': 'Authentication',
    'depends': ['auth_signup', 'base_setup', 'web'],
    'data': [
        #"view/home.xml"
    ],
    'installable': True,
    'auto_install': False,
}
