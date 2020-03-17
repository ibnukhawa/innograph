
# -*- coding: utf-8 -*-
{
    'name': 'Innograph Custom Website Favicon',
    'version': '10.0.1.0.0',
    'license': 'AGPL-3',
    "author": "Port Cities",
    'category': 'eCommerce',
    'summary': 'Customizing for favicon multi website',
    'contributors': [
        'Alfif Nurmirza Maulana',
    ],
    'description': """
        Customizing for favicon multi website jut in frontend website

    """,
    'depends': [
        'website','pqm_website_access',
        'web'],
    'data': [                                                         
        'views/inherit_favicon.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False
}

