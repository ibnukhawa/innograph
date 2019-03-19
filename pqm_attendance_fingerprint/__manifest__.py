# -*- coding: utf-8 -*-
{
    'name': 'PQM Base Attendance',
    'version': '10.0.1.0.0',
    'author': 'Portcities Ltd',
    'website': 'http://www.portcities.net',
    'summary': "PQM Custom Attendance Core",
    'contributors': [
        'Syarifudin Akbar',
        'Dhimas Yudangga A',
    ],
    'description': """
    Add fingerprint module support to hr, and attendance report in website portal
    """,
    'category': 'PQM PHASE 3',
    'sequence': 1,
    'depends': [
        'hr_attendance', 
        'hr', 
        'resource',
        'pqm_portal_base',
        'hr_timesheet_attendance'
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/function_attendance_init_plan.xml',
        'views/hr_attendance_view.xml',
        'views/hr_employee_view.xml',
        'views/resource_calendar_view.xml'
    ],
    'auto_install': False,
    'installable': True,
    'application': False,
}
