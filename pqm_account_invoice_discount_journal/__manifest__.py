# pylint: disable=C0111,I0011
# -*- coding: utf-8 -*-
{
    'name': 'PQM: Journal Invoice with Discount',
    'author': 'Portcities',
    'website': 'http://portcitiesindonesia.com',
    'category': 'account',
    'version': '10.0.1.0.0',
    'depends': ['account', 'pqm_project_code'],
    'description': '''
        V.1 \n
        - Generate journal item with discount account when validating invoice with discount
        
        Contributor by : SM
        
        V.2 \n
        -  Generate invoice from sales order with value Discount Account from project type of project on sale order
        
        Contributor by : Hasyim
    ''',
    'data': [
        'views/account_journal.xml',
        'views/account_invoice.xml'
    ],
    'installable': True,
    'active': False,
    'auto_install': False
}
