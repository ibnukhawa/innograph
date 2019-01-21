# -*- coding: utf-8 -*-
{
    'name'          : 'Innograph Access Right',
    'version'       : '10.0.1.0',
    "author"        : "Port Cities",
    'category'      : 'General',
    'summary'       : 'Access Right for Innograph',
    'sequence'      : 1,
    'description'   : """
        *Author : Dwiki Adnan F.
    """,
    'depends'       : ['hr', 'hr_contract'],
    'data'          : [
                        'data/employee_rule_data.xml',
                        'views/hr_employee_view.xml',
                      ],
    'installable'   : True,
    'application'   : True,
    'auto_install'  : False
}
