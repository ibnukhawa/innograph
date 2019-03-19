# -*- coding: utf-8 -*-
{
    'name'          : 'Innograph Partner',
    'version'       : '10.0.1.0.0',
    'author'        : 'Port Cities',
    'category'      : 'Purchase',
    'summary'       : 'Innograph Vendor',
    'sequence'      : 1,
    'depends'       : ['purchase', 'efaktur', 'sales_team'],
    'data'          : [
        'security/ir.model.access.csv',
        'views/res_partner_view.xml',
    ],
    'installable'   : True,
    'application'   : True,
    'auto_install'  : False
}
