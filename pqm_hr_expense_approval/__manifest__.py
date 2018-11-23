# pylint: disable=C0111,I0011
# -*- coding: utf-8 -*-
##############################################################################
#
#   Odoo, Open Source Management Solution
#   Copyright (C) 2017 Port Cities International
#   Author : www.portcities.net
#
##############################################################################

{
    'name': 'PQM hr expense approval',
    'version': '1.0',
    'author': 'Portcities.Ltd',
    'description': """
v1.0
----
* Add validator and Approval on Expenses
* Generate Expense by Product Category
* Add notif to validator and approval
    
    Author : AFH \n
    """,
    'website': 'http://www.portcities.net',
    'depends': ['pci_hr_expense_validate'],
    'category': 'HR Expenses',
    'data': [
             'data/expense_submit_email_template.xml',
             'data/expense_validate_email_template.xml',
             'views/res_users_view.xml',
             'views/product_category_view.xml',
             'views/hr_expense_view.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
