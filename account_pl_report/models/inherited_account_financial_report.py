# -*- coding: utf-8 -*-

import time
from odoo import api, models, fields

class account_financial_report(models.Model):
    _inherit = 'account.financial.report'
    
    show_root_balance = fields.Boolean('Show Balance')
    title_root_balance = fields.Char('Title Balance')