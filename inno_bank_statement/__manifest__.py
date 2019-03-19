# -*- coding: utf-8 -*-
{
    'name': 'Innograph Bank Statement',
    'version': '10.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Port Cities Ltd',
    'website': 'https://www.portcities.net',
    'category': 'Accounting',
    'summary': 'Bank Statement Report',
    'depends': ['account', 'report_xlsx'],
    'data': [
        'reports/report_bank_statement.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
