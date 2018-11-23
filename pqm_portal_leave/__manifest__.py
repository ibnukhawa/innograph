# -*- coding: utf-8 -*-
{
    'name': 'PQM Base Leaves',
    'version': '10.0.1.0.0',
    'author': 'Portcities Ltd',
    'website': 'http://www.portcities.net',
    'contributors': [
        'Reynaldi Yosfino',
        'Dhimas Yudangga A',
    ],
    'summary': "PQM Custom Leaves",
    'description': """
    Add leave module functionality in website portal
    """,
    'category': 'PQM PHASE 3',
    'sequence': 1,
    'depends': [
        'hr_holidays', 
        'hr', 
        'pqm_portal_base',
        'mail',
    ],
    'data': [
        'data/email_notification.xml',
        'data/mail_message_subtype_data.xml',
        'views/hr_employee_view.xml',
        'views/hr_leaves_web_template.xml'
    ],
    'auto_install': False,
    'installable': True,
    'application': False,
}
