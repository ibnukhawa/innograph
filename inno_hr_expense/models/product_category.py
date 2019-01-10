# -*- coding: utf-8 -*-
""" Import """
from odoo import fields, models


class ProductCategory(models.Model):
    """ Inherit Product Category """
    _inherit = 'product.category'

    is_medical = fields.Boolean()
