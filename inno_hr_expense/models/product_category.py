# -*- coding: utf-8 -*-
from odoo import fields, models

class ProductCategory(models.Model):
    _inherit = 'product.category'

    is_medical = fields.Boolean(string="Is Medical")    
