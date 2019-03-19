# -*- coding: utf-8 -*-
{
    'name': 'PQM Attendance Report',
    'version': '10.0.1.0.0',
    'author': 'Portcities Ltd',
    'website': 'http://www.portcities.net',
    'summary': "PQM Custom Attendance Report",
    'contributors': [
        'Syarifudin Akbar',
        'Dhimas Yudangga A',
    ],
    'description': """
    Add attendance and leave report
    """,
    'category': 'PQM PHASE 3',
    'sequence': 1,
    'depends': [
        'pqm_attendance_fingerprint',
    ],
    'data': [
        'report/attendance_report.xml',
        'wizard/attendance_wizard_view.xml'
    ],
    'auto_install': False,
    'installable': True,
    'application': False,
}
