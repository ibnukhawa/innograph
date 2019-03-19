# -*- coding: utf-8 -*-
{
    'name': 'PQM Portal Daily Attendance',
    'version': '10.0.1.0.0',
    'author': 'Portcities Ltd',
    'website': 'http://www.portcities.net',
    'contributors': [
        'Alvin Adji',
        'Dhimas Yudangga A',
    ],
    'summary': "Custom Website Footer",
    'description': """
    Custom Website Footer with Attendance Table and Chart
    Note : to apply this footer Activate Automatic Footer and then Choose Footer with Attendance
    """,
    'category': 'PQM PHASE 3',
    'sequence': 1,
    'depends': [
        'pqm_attendance_fingerprint',
    ],
    'data': [
        'views/asset.xml',
        'views/footer.xml',
        'views/daily_attendance_page.xml'
    ],
    'auto_install': False,
    'installable': True,
    'application': False,
}
