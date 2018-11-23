# -*- coding: utf-8 -*-
{
    'name': 'PQM Leave Report',
    'version': '10.0.1.0.0',
    'author': 'Portcities Ltd',
    'website': 'http://www.portcities.net',
    'summary': "PQM Custom Leave Report",
    'contributors': [
        'Reynaldi Yosfino',
        'Dhimas Yudangga A',
    ],
    'description': """
    Add leave report
    """,
    'category': 'PQM PHASE 3',
    'sequence': 1,
    'depends': [
        'hr_holidays', 
        'hr',
    ],
    'data': [
        'views/hr_holidays_status_view.xml',
        'report/leave_report.xml',
        'wizard/leave_wizard_view.xml'
    ],
    'auto_install': False,
    'installable': True,
    'application': False,
}
