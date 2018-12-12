# -*- coding: utf-8 -*-
{
    'name'          : 'Innograph Global Discount',
    'version'       : '10.0.1.0',
    "author"        : "Port Cities",
    'category'      : 'Account',
    'summary'       : 'innograph customization on global discount',
    'sequence'      : 1,
    'description'   : """
        *Author : Dhimas Yudangga A.
    """,
    'depends'       : ['base', 'product', 'sale', 'account', 'project'],
    'data'          : [
        'views/product_template_views.xml',
        'views/sale_order_views.xml',
        'views/account_invoice_views.xml',
    ],
    'application'   : False,
    'auto_install'  : False,
    'installable'   : True,
}
