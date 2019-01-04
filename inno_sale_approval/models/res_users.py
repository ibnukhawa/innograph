# -*- coding: utf-8 -*-
from odoo import fields, models

class Users(models.Model):
    _inherit = "res.users"
    
    sale_order_discount_limit = fields.Float("(SO) Discount Limit", digits=(16, 2), required=True)
