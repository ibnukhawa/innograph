# -*- coding: utf-8 -*-
"""pqm_hr_expense_approval"""
from odoo import models, fields, api, _

class ProductCategory(models.Model):
    """class product category"""
    _inherit = "product.category"

    validate_id = fields.Many2one('res.users', string="Validate User", domain=[('is_validator', '=', True)])
    is_expenses = fields.Boolean()