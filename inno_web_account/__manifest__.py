{
    'name': 'Innograph Custom Website Breadcrumb',
    'version': '1.0',
    'category': 'Website',
    'summary': "Customizing eCommerce website breadcrumb",
    'author': 'Portcities Ltd',
    'company': 'Portcities Ltd',
    'website': 'http://www.portcities.net',
    'description': """
        Custom breadcrumb
    """,
    'depends': [
            'website',
            'theme_stoneware',
            'website_sale',
            'website_blog',
            'website_event',
            'website'
    ],
    'data': [
        'views/custom_breadcrumb.xml',
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
}
