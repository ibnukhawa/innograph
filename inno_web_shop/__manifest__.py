# -*- coding: utf-8 -*-
{
    'name': 'Innograph Custom Website Shop',
    'version': '10.0.1.0.0',
    'license': 'AGPL-3',
    "author": "Port Cities",
    'category': 'eCommerce',
    'summary': 'Customizing eCommerce website Shop for grid and style product',
    'contributors': [
        'Alfif Nurmirza Maulana',
    ],
    'description': """
        Customizing eCommerce website Shop for grid and style product
    """,
    'depends': [
        'website_sale',
        'web',
        'theme_stoneware'],
    'data': [
        'views/custom.xml',
		# 'security/ir.model.access.csv',                                                         
        # 'views/product_category_view.xml',
        # 'views/homepage.xml',
		# 'views/website_admin.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False
}

