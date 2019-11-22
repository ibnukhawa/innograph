# -*- coding: utf-8 -*-
from odoo import fields, models

class ResCompany(models.Model):
    _inherit = 'res.company'

    lkpp_government_pricelist_id = fields.Many2one(
        string="Government Pricelist",
        comodel_name='product.pricelist',
    )
    default_website_pricelist_id = fields.Many2one(
        string="Default Website Pricelist",
        comodel_name='product.pricelist',
    )
