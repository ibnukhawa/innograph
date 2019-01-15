# -*- coding: utf-8 -*-
{
    'name': 'Innograph HR Expense',
    'version': '10.0.1.0.0',
    'author': 'Port Cities',
    'category': 'Purchase',
    'summary': 'HR Expense custom',
    'sequence': 1,
    'depends': ['pqm_hr_expense_approval'],
    'data': [
        'views/hr_view.xml',
        'views/product_category_view.xml',
        'report/hr_expense_report.xml',
        'wizard/hr_expense_medical_confirmation_view.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': False
}
