# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Custom General Ledger',
    'version': '1.0',
    'category': 'Accounting',
    'description': """
Author : Septia Devi Cahyaningtias
    - Add Without movements to display account
    - Display view only account bank when journals bank selected

Contributor : Saiful Rijal
    - Adjust layout in general ledger report :
        - move line total per account after move line of each account
        - remove column JRNL 

Contributor : AFH
    - Generate Report Excel General Ledger

Contributor : Irwinda
    - Adjust layout in general ledger report : 
        - add column WBS code
        - replace Journals on report header with Accounts


""",
    'author': 'Port Cities',
    'website': '',
    'depends': [ 'base', 'account', 'base_setup', 'product', 'analytic', 'report', 'pci_account_general_ledger_filter'],
    'data': [
             'wizard/custom_general_ledger.xml',
            'views/custom_general_ledger_report.xml',
            'views/custom_view.xml',
    ],
    'demo' : [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
