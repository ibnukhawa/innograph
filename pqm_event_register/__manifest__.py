# -*- coding: utf-8 -*-
{
    'name': 'PQM Event Register',
    'version': '10.0.1.0.0',
    'author': 'Portcities Ltd',
    'website': 'http://www.portcities.net',
    'summary': "PQM Custom Event Register",
    'contributors': [
        'Saiful Rijal',
        'Dhimas Yudangga A',
    ],
    'description': """
    - register form\n
    """,
    'category': 'PQM PHASE 4',
    'sequence': 1,
    'depends': [
        'event',
        'pqm_event_core',
        'efaktur',
        'website_event_sale',
        'theme_impacto',
    ],
    'data': [
        'views/register_templates.xml',
        'views/res_partner_views.xml',
        'views/website_sale_template.xml',
    ],
    'auto_install': False,
    'installable': True,
    'application': False,
}
