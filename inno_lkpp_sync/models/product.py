# -*- coding: utf-8 -*-
from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    unspsc = fields.Char(string='UNSPSC', size=8)
    active_product = fields.Boolean()
    local_product = fields.Boolean()
    valid_date = fields.Date(string='Valid Until')
    specification = fields.Text()

    lkpp_category_id = fields.Char(string='Category')
    lkpp_manufacturer_id = fields.Char(string='Manufacturer')

    lkpp_sell_price = fields.Float(string='Sell Price')
    lkpp_govt_price = fields.Float(string='Goverment Price')


class ProductUoM(models.Model):
    _inherit = 'product.uom'

    lkpp_uom_id = fields.Char()
