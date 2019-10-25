
# -*- coding: utf-8 -*-
{
    'name': 'Innograph Custom Website Homepage',
    'version': '10.0.1.0.0',
    'license': 'AGPL-3',
    "author": "Port Cities",
    'category': 'eCommerce',
    'summary': 'Customizing eCommerce website Homepage',
    'contributors': [
        'Alfif Nurmirza Maulana',
    ],
    'description': """
        Custome homepage with slider slick
    """,
    'depends': [
        'website_sale',
        'website_mass_mailing',
        'website_blog',
        'website_event',
        'web','web_editor',
        'website_slides'],
    'data': [
		'security/ir.model.access.csv',                                                         
        'views/product_category_view.xml',
        'views/homepage.xml',
		'views/website_admin.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': False
}

