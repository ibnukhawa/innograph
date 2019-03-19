{
    'name': 'Custom Report Order Pembelian',
    'version': '10.0.1.0.5',
    'author': 'Portcities',
    'summary': '',
    'description': """
        Custom Report Pembelian Order
        v.1.0.5\n
        Update style, add PPN, PPH on the report view.
        \n
        author:Wisnu
        
    Contributor : M.Hasyim.Yahya
    - Adjust purchase order report :
        -add field digital_signature,is_approver,Add domain on field approver in PO
        -Adjust function button_approve:update value field approver with user active and put digital signature
        
    Contributor : Syarif
    - add email for creator and approver 
    - add custom confirm button behaviour
    - add approver behaviour
    
    """,
    'depends': ['base', 'purchase', 'amount_to_text_id'],
    'data': [
        'views/report_order_pembelian.xml',
        'views/res_partner_view.xml',
        'views/purchase_order_view.xml',
        'data/email_po_template.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'qweb': [],
}
