{
    'name': 'Innograph Custom Website Header',
    'version': '1.0',
    'category': 'Website',
    'summary': "Customizing eCommerce website header",
    'author': 'Portcities Ltd',
    'company': 'Portcities Ltd',
    'website': 'http://www.portcities.net',
    'description': """
        Custom header website
    """,
    'depends': ['website',
            'theme_stoneware',
            'website_sale',
            'website_blog',
            'website_event',
            'website'
    ],
    'data': [
        'views/template_header.xml',
        'views/custom_template.xml',
        'views/assets.xml',
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
}
