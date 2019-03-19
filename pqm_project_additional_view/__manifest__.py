# -*- coding: utf-8 -*-

{
    'name': 'PQM Project Additional view',
    'version': '10.0.1.0.0',
    'author': 'Port Cities',
    'website': 'http://www.portcities.net',
    'summary': "PQM Project",
    'description': """
v1.0
----
* Add Account Manager on project project \n
* Show field Start Date and Expiraation Date \n

    * Author : AFH
v1.1
----
* Add Auto mail for follower after create new project and archive project \n

    * Author : Yatiman
       
    """,
    'category': 'project',
    'sequence': 1,
    'license': 'AGPL-3',
    'depends': ['project'],
    'data': [
        'views/project_project_views.xml',
        'data/auto_email_template.xml'
    ],


    'auto_install': False,
    'installable': True,
    'application': False,
}
