# -*- coding: utf-8 -*-
{
    'name'          : 'Innograph Partner',
    'version'       : '10.0.1.0',
    "author"        : "Port Cities",
    'category'      : 'Purchase',
    'summary'       : 'Innograph Vendor',
    'sequence'      : 1,
    'description'   : """
    - Add new model Line of Business on Purchase \n
    - Add new field Vendor Specialization on Partner \n
    - Add new field Product Specialization on Partner \n
    - Add new field Line of Business on Partner \n
    - Add new field No PKP on Partner \n
        *Author : Dwiki Adnan F.
    """,
    'depends'       : ['purchase', 'efaktur'],
    'data'          : [
                        'security/ir.model.access.csv',
                        'views/res_partner_view.xml',
                      ],
    'installable'   : True,
    'application'   : True,
    'auto_install'  : False
}
