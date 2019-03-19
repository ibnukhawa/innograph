# -*- coding: utf-8 -*-
{
    'name': 'PQM Base Portal',
    'version': '10.0.1.0.0',
    'author': 'Portcities Ltd',
    'website': 'http://www.portcities.net',
    'contributors': [
        'Dhimas Yudangga A',
    ],
    'summary': "PQM Portal Core",
    'description': """
    Add some modification to base portal route
    """,
    'category': 'PQM PHASE 3',
    'sequence': 1,
    'depends': [
        'website_portal_sale', 
    ],
    'data': [
        'views/portal_templates.xml'
    ],
    'auto_install': False,
    'installable': True,
    'application': False,
}
