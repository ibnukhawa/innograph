# -*- coding: utf-8 -*-
{
    'name': 'PQM Portal Filter',
    'version': '10.0.1.0.0',
    'author': 'Portcities Ltd',
    'website': 'http://www.portcities.net',
    'contributors': [
        'Syarifudin Akbar',
    ],
    'summary': "PQM Portal Filter",
    'description': """
    Add filter to portal quotation, order and invoice to only can see by create_uid and partner_id
    """,
    'category': 'PQM PHASE 3',
    'sequence': 1,
    'depends': [
        'pqm_portal_base',
    ],
    'auto_install': False,
    'installable': True,
    'application': False,
}
