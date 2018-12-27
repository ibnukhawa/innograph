# -*- coding: utf-8 -*-
{
    'name'          : 'Innograph Product',
    'version'       : '10.0.1.0',
    "author"        : "Port Cities",
    'category'      : 'Product',
    'summary'       : 'Product Category',
    'sequence'      : 1,
    'description'   : """
        
        *Author : Dwiki Adnan F.
    """,
    'depends'       : ['product', 'purchase', 'sales_team', 'account'],
    'data'          : [
                        'security/ir.model.access.csv',
                        'views/product_category_view.xml',
                        'views/product_view.xml'
                      ],
    'installable'   : True,
    'application'   : True,
    'auto_install'  : False
}
