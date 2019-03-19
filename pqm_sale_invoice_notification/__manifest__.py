# -*- coding: utf-8 -*-
{
    'name': 'PQM Sale Invoice Notification',
    'version': '10.0.1.0.0',
    'author': 'Port Cities',
    'website': 'http://www.portcities.net',
    'summary': "PQM Sale Invoice Notification",
    'description': """
v1.0
----
* Add project follower, accounting billing, director and administrator become
follower of sale order and invoice. \n
* automatically sending email to follower when the sale order's state changed
to sale order, invoice's state changed to open and paid.\n

    * Author : Andreas DSP
    """,
    'category': 'mail',
    'sequence': 1,
    'license': 'AGPL-3',
    'depends': ['base', 'mail', 'sale'],
    'data': [
        'data/sale_order_email_notification.xml',
        'data/invoice_open_email_notification.xml',
        'data/invoice_paid_email_notification.xml',
        'views/res_users_view.xml',
    ],
    'auto_install': False,
    'installable': True,
    'application': False,
}
