# -*- coding: utf-8 -*-
{
    'name'          : 'Innograph Sales Order Report',
    'version'       : '10.0.1.0',
    "author"        : "Port Cities",
    'category'      : 'Sales',
    'summary'       : 'Sales Order Report',
    'sequence'      : 100,
    'description'   : """
        *Author : Dwiki Adnan F.
    """,
    'depends'       : [
        'inno_sales_order', 
    ],
    'data'          : [
        'wizard/sale_order_report_wizard_view.xml'
    ],
    'installable'   : True,
    'application'   : True,
    'auto_install'  : False
}
