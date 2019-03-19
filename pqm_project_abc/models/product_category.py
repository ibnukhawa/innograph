# -*- coding: utf-8 -*-
""" pqm_project_abc """
from odoo import fields, models

class ProductCategory(models.Model):
    """ Class Product Category """
    _inherit = "product.category"

    is_abc = fields.Boolean(string='Implement ABC')
