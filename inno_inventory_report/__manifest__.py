# -*- coding: utf-8 -*-
{
    'name': 'Innograph Inventory Report',
    'version': '10.0.1.0.0',
    "author": "Port Cities",
    'category': 'Inventory',
    'summary': 'Custom Inventory Report',
    'sequence': 1,
    'description': """
        Add Custom Delivery Report (DO/Receipt) \n
        Add Custom Delivery Slip \n
        *Author : Dwiki Adnan F.
    """,
    'depends': ['stock'],
    'data': [
        'report/delivery_order_report.xml',
        'report/delivery_slip_report.xml',
        'views/stock_picking_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False
}
