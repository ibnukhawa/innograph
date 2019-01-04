# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, SUPERUSER_ID, _

class Users(models.Model):
    _inherit = "res.users"
    
    sale_order_discount_limit = fields.Float("(SO) Discount Limit", digits=(16, 2), required=True)
