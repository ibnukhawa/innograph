# -*- coding: utf-8 -*-

{
    'name': 'PQM Project ABC',
    'version': '10.0.1.0.0',
    'author': 'Portcities Ltd',
    'website': 'https://www.portcities.net',
    'category': 'Project',
    'license': 'AGPL-3',
    'summary': 'Implement Activity Based costing project',
    'description': """
    Generate Journal items cost of employee when validate customer invoice and
    change income account on invoice lineto income account of project type
    By: IK\n

    v2.0:\n
    - Add condition for timesheet hours\n
    - Remove Analytic Account for Tax in Journal Entries\n
    By Ardha
    """,
    'depends': ['account', 'project', 'pqm_project_code'],
    'data': [
#        'views/product_category.xml',
        'views/hr_employee.xml',
        'views/project_config_settings.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
