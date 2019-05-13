# -*- coding: utf-8 -*-
{
    'name': 'PQM Website Access',
    'version': '10.0.1.0.0',
    'author': 'Portcities Ltd',
    'website': 'http://www.portcities.net',
    'contributors': [
        'Dhimas Yudangga A',
        'Syarifudin Akbar'
    ],
    'summary': "PQM Website Access",
    'description': """
    Modify menu access in website
    """,
    'category': 'PQM PHASE 3',
    'sequence': 1,
    'depends': [
        'website', 'website_sale', 'website_event'
    ],
    'data': [
        'data/event_mail_template_data.xml',
        'security/ir.model.access.csv',
        'views/website_menu_views.xml',
        'views/website_templates.xml',
        'views/origin_url_view.xml',
    ],
    'auto_install': False,
    'installable': True,
    'application': False,
}
