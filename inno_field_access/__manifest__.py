# -*- coding: utf-8 -*-
{
    'name'          : 'Innograph Field Access Right',
    'version'       : '10.0.1.0',
    "author"        : "Port Cities",
    'category'      : 'General',
    'summary'       : 'Field Access Right for Innograph',
    'sequence'      : 1,
    'description'   : """
        *Author : Dwiki Adnan F.
    """,
    'depends'       : ['purchase', 'sale', 'project', 'account', 'custom_kwitansi_report'],
    'data'          : [
                        'views/field_access_view.xml',
                      ],
    'installable'   : True,
    'application'   : True,
    'auto_install'  : False
}
