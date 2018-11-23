# -*- coding: utf-8 -*-
{
    'name': 'PQM Custom Access',
    'version': '10.0.1.0.0',
    'author': 'Portcities Ltd',
    'website': 'http://www.portcities.net',
    'summary': "PQM Custom Access",
    'description': """
v1.0
----
    - Add security access on detail timesheet (account.analytic.line) and hr_employee for employee user\n
    - Add security access (rule) on Purchase Order
    By Ilham

    """,
    'category': 'hr',
    'sequence': 1,
    'license': 'AGPL-3',
    'depends': ['hr','hr_holidays', 'hr_timesheet_sheet', 'hr_contract', 'purchase',
                'hr_grade_rank', 'pqm_project_abc', 'hr_employee_updation',
                'hr_attendance', 'hr_employee_seniority', 'hr_gamification', 'custom_kwitansi_report'],
    'data': [
        'security/ir.model.access.csv',
        'security/ir_rule_security.xml',
        'views/hr_employee.xml',
        'views/sale_order.xml'
    ],

    'auto_install': False,
    'installable': True,
    'application': False,
}
