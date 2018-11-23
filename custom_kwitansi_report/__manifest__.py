# -*- coding: utf-8 -*-
{
    'name': 'Custom Kwitansi',
    'version': '10.0.1.1.0',
    'category': 'Accounting',
    'license': 'AGPL-3',
    'description': """
    Custom Kwitansi
        Create Kwitansi report as qweb(pdf) customed
        by. Wisnu Sadewo
        
        Update: Saiful dan Dion
    """,
    'author': 'Portcities',
    'website': 'http://www.portcities.net',
    'depends': ['base', 'account', 'base_setup', 'product',
                'analytic', 'report', 'sale', 'purchase','vit_inv_label'],
    'data': [
        'data/ir_sequence_data.xml',
        'report/custom_kwitansi_report_view.xml',
        'report/report_kwitansi.xml',
        'report/custom_invoice_report_view.xml',
        'views/account_payment_view.xml',
        'views/res_company_view.xml',

    ],
    'demo' : [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
