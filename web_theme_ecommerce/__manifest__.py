{
    'name': 'Website Theme Ecommerce',
    'category': 'Theme/Ecommerce',
    'summary': "Website Theme Ecommerce",
    'version': '1.1',
	'license' : 'OPL-1',
    'author': 'portcities.net',
	'website': 'https://www.portcities.net',
	'support': 'porcities.net',
    'description': """

        """,
    'depends': ['website_sale','website_mass_mailing','website_crm','website_blog','website_event','pqm_website_access','web','theme_stoneware'],
    'data': [
		'security/ir.model.access.csv',                                                         
        'views/product_category_view.xml',
        'views/homepage.xml',
		'views/website_admin.xml',
    ],
    'installable': True,
	'application': True,
}
