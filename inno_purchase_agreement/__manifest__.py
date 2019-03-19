# -*- coding: utf-8 -*-
{
    'name'          : 'Innograph Purchase Agreement',
    'version'       : '10.0.1.0',
    "author"        : "Port Cities",
    'category'      : 'Purchase',
    'summary'       : 'Purchase Agreement',
    'sequence'      : 1,
    'description'   : """
        Change Purchase Agreement to Purchase Request \n
        Change field on Purchase Agreement \n
        Change Prefix on Purchase Agreement \n
        Add field Approver on Purchase Request \n
        Add feature notification when Confirm and Validate Purchase Requests \n
        *Author : Dwiki Adnan F.
    """,
    'depends'       : ['purchase_requisition'],
    'data'          : [
                        'data/purchase_requisition_data.xml',
                        'data/purchase_request_email_template.xml',
                        'views/purchase_requisition_view.xml',
                        'views/res_partner_view.xml',
                      ],
    'installable'   : True,
    'application'   : True,
    'auto_install'  : False
}
