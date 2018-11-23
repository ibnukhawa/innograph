# -*- coding: utf-8 -*-
{
    'name': 'PQM Project Code',
    'version': '10.0.1.0.0',
    'author': 'Port Cities',
    'website': 'http://www.portcities.net',
    'summary': "PQM Project Code",
    'description': """
v1.0
----
* Add project Type and project SME on project project \n
* automatically generate prefix sequence based on
code in project type and project sme.\n

    * Author : IK

v1.1
----
* Add project Sub SME on project project \n
* Add Description on Project Type, Project SME, and Project Sub SME \n

    * Author : IK

    """,
    'category': 'project',
    'sequence': 1,
    'license': 'AGPL-3',
    'depends': ['project', 'account', 'analytic', 'account_analytic_parent'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/project_margin.xml',
        'views/project_project_view.xml',
        'views/project_type_view.xml',
        'views/project_sme_view.xml',
        'views/project_sub_sme_view.xml',
        'report/report.xml',
        'report/project_margin_report.xml'
    ],
    'auto_install': False,
    'installable': True,
    'application': False,
}
