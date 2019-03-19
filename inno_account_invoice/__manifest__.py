# -*- coding: utf-8 -*-
{
    'name'          : 'Innograph Invoice',
    'version'       : '10.0.1.0',
    "author"        : "Port Cities",
    'category'      : 'Account',
    'summary'       : 'innograph customization on Invoice',
    'sequence'      : 1,
    'description'   : """
        *Author : Dwiki Adnan F.
    """,
    'depends'       : ['account'],
    'data'          : [
        'views/account_invoice_views.xml',
    ],
    'application'   : False,
    'auto_install'  : False,
    'installable'   : True,
}
