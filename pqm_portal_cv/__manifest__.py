# -*- coding: utf-8 -*-
{
    'name': 'PQM Base Curriculum Vitae',
    'version': '10.0.1.0.0',
    'author': 'Portcities Ltd',
    'website': 'http://www.portcities.net',
    'contributors': [
        'Reynaldi Yosfino',
        'Dhimas Yudangga A',
    ],
    'summary': "PQM Custom Curriculum Vitae",
    'description': """
    Add feature to edit personal information functionality in website portal
    """,
    'category': 'PQM PHASE 3',
    'sequence': 1,
    'depends': [
        'hr_holidays', 
        'hr', 
        'pqm_portal_base',
        'hr_employee_display_own_info',
    ],
    'data': [
        'views/hr_employee_web_template.xml'
    ],
    'auto_install': False,
    'installable': True,
    'application': False,
}
