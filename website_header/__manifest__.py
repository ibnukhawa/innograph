{
    'name': 'Website Header',
    'version': '1.0',
    'category': 'Website',
    'summary': "Header on Website",
    'author': 'Portcities Ltd',
    'company': 'Portcities Ltd',
    'website': 'http://www.portcities.net',
    'description': """
        Custom header website
    """,
    'depends': ['website',
            'theme_stoneware',
            'website_sale','website_mass_mailing','website_crm','website_blog','website_event'
    ],
    'data': [
        # 'views/home.xml',
        # 'views/homepage.xml',
        'views/template_header.xml',
        'views/custom_template.xml',
        'views/assets.xml',
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
}
