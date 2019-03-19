# -*- coding: utf-8 -*-
{
    'name': 'PQM Account Invoice Proforma',
    'version': '10.0.1.0.0',
    'author': 'Portcities Ltd',
    'website': 'http://www.portcities.net',
    'summary': "Deferred Revenue (Accrued Income)",
    'description': """
v1.0
----
    - Feature Defered Revenue

    """,
    'category': 'Accounting',
    'sequence': 1,
    'license': 'AGPL-3',
    'depends': ['pci_account_invoice_proforma', 'pqm_project_code'],
    'data': [
        'views/project_type_view.xml',
        'views/account_invoice_view.xml'
    ],

    'auto_install': False,
    'installable': True,
    'application': False,
}
