# -*- coding: utf-8 -*-
{
    'name'          : 'Innograph MRP BOM Versioning',
    'version'       : '10.0.1.0',
    "author"        : "Port Cities",
    'category'      : 'Manufacture',
    'summary'       : 'BOM Versioning',
    'sequence'      : 1,
    'description'   : """
    Add New Feature Bill of Material Revision \n
        *Author : Dwiki Adnan F.
    """,
    'depends'       : ['mrp'],
    'data'          : [
                        'security/ir.model.access.csv',
                        'views/mrp_bom_revision_view.xml',
                      ],
    'installable'   : True,
    'application'   : True,
    'auto_install'  : False
}
