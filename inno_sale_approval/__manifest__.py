# -*- coding: utf-8 -*-
{
    'name': 'Innograph Quotations/Sales Orders Approval',
    'version': '10.0.1.0',
    'category': 'Sales',
    'sequence': 1,
    'summary': 'Quotations/Sales Orders Approval',
    'description': """
        Manage sales quotations and orders Approval.
    """,
    'website': 'https://portcities.net',
    'author': 'Portcities Ltd',
    'depends': ['base_setup', 'sale', 'sales_team', 'sale_approval'],
    'data': [
        'views/sale_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
