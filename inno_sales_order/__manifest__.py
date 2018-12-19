# -*- coding: utf-8 -*-
{
    'name'          : 'Innograph Sales Order',
    'version'       : '10.0.1.0',
    "author"        : "Port Cities",
    'category'      : 'Sales',
    'summary'       : 'Sales Order Report',
    'sequence'      : 100,
    'description'   : """
        *Author : Dwiki Adnan F.
    """,
    'depends'       : [
        'sale_stock', 
        'report', 
        'inno_account_invoice_discount_journal'
    ],
    'data'          : [
        "report/sale_order_report.xml",
        "report/sale_order_report_template.xml"
    ],
    'installable'   : True,
    'application'   : True,
    'auto_install'  : False
}
