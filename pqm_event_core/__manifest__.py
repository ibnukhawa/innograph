# -*- coding: utf-8 -*-
{
    'name': 'PQM Base Event',
    'version': '10.0.1.0.0',
    'author': 'Portcities Ltd',
    'website': 'http://www.portcities.net',
    'summary': "PQM Custom Event Core",
    'contributors': [
        'Dwiki Adnan F.',
        'Dhimas Yudangga A',
    ],
    'description': """
    Website Card and Calendar view on Event
    """,
    'category': 'PQM PHASE 4',
    'sequence': 1,
    'depends': [
        'event', 
        'website_event', 
        'website_event_sale',
        'website_event_track',
        'pqm_project_code',
        'theme_impacto',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/event_target_data.xml',
        'data/email_reply_template.xml',
        'views/res_partner_view.xml',
        'views/event_event_view.xml',
        'views/crm_lead_view.xml',
        'views/events_templates.xml',
        'views/sale_order_report_template.xml',
        'wizard/comment_reply_wizard_view.xml'
    ],
    'auto_install': False,
    'installable': True,
    'application': False,
}