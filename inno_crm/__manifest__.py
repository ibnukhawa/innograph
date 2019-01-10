# -*- coding: utf-8 -*-
{
    'name': 'Innograph CRM',
    'version': '10.0.1.0.0',
    "author": "Port Cities",
    'category': 'CRM',
    'summary': 'Custom CRM',
    'sequence': 1,
    'description': """
        *Author : Dwiki Adnan F.
    """,
    'depends': ['crm_opportunity_product', ],
    'data': ['views/crm_stage_view.xml'],
    'installable': True,
    'application': True,
    'auto_install': False
}
