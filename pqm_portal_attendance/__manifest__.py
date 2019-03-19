# -*- coding: utf-8 -*-
{
    'name': 'PQM Portal Attendance',
    'version': '10.0.1.0.0',
    'author': 'Portcities Ltd',
    'website': 'http://www.portcities.net',
    'summary': "PQM Custom Attendance Portal",
    'contributors': [
        'Syarifudin Akbar',
        'Dhimas Yudangga A',
    ],
    'description': """
    Add attendance report in website portal
    """,
    'category': 'PQM PHASE 3',
    'sequence': 1,
    'depends': [
        'pqm_attendance_fingerprint',
        'pqm_portal_leave',
    ],
    'data': [
        'data/function_coach_attendance.xml',
        'data/email_attendance_template.xml',
        'views/hr_attendance_web_template.xml'
    ],
    'auto_install': False,
    'installable': True,
    'application': False,
}
