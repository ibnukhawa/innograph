# -*- coding: utf-8 -*-
{
    'name': 'Sale Invoice Date',
    'version': '10.0.1.0.0',
    'author': 'Portcities Ltd',
    'website': 'http://www.portcities.net',
    'summary': "Input Invoice Date by sales",
    'description': """
v1.0
----
    - Sales will inout invoice date on wizard create invoice
    -- AFH --

    """,
    'category': 'Accounting',
    'sequence': 1,
    'license': 'AGPL-3',
    'depends': ['sale', 'account',],
    'data': [
        'wizard/sale_advance_payment_inv_views.xml',
    ],

    'auto_install': False,
    'installable': True,
    'application': False,
}
