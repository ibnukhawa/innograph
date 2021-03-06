# -*- coding: utf-8 -*-
{
    'name'          : 'Innograph Purchase Order',
    'version'       : '10.0.1.0',
    "author"        : "Port Cities",
    'category'      : 'Purchase',
    'summary'       : 'Purchase Order',
    'sequence'      : 1,
    'description'   : """
        *Author : Dwiki Adnan F.
    """,
    'depends'       : ['custom_order_pembelian', 'calendar', 'purchase_discount'],
    'data'          : [
                        'data/inno_purchase_order_data.xml',
                        'views/purchase_view.xml',
                        'report/purchase_order_report.xml',
                        'report/purchase_order_report_template.xml',
                      ],
    'installable'   : True,
    'application'   : True,
    'auto_install'  : False
}
