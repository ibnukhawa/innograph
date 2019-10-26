{
    'name': 'Cropper Image',
    'summary': """
        Cropper Image
        """,
    'version': '0.0.1',
    'category': 'web',
    "author": "La Jayuhni Yarsyah",
    'description': """
        Cropper image useing Cropper.js
    """,
    'depends': [
        'web','web_editor'
    ],
    'data': [
    	'views/assets.xml',
    ],
    'qweb':[
    	# 'static/src/xml/editor.xml',
        'static/src/xml/cropper_backend.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True    
}