# -*- coding: utf-8 -*-
from odoo import fields, models, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    unspsc = fields.Char(string='UNSPSC', size=8)
    active_product = fields.Boolean()
    local_product = fields.Boolean()
    valid_date = fields.Date(string='Valid Until')
    specification = fields.Text()

    lkpp_category_id = fields.Char(string='Category')
    lkpp_manufacturer_id = fields.Char(string='Manufacturer')

    # lkpp_sell_price = fields.Float(string='Sell Price')

    lkpp_govt_price = fields.Float(string='Goverment Price',compute='_computed_price_goverment')
    website_price_new = fields.Float(string='Sale Price',readonly=False)

    list_price = fields.Float(string='Website Price',compute='_computed_price_website')


    @api.depends("website_price_new")
    def _computed_price_website(self):
        for record in self:
            price = record.website_price_new + (record.website_price_new * 0.1)

            record.list_price = price

    @api.depends("website_price_new")
    def _computed_price_goverment(self):
        for record in self:
            price = record.website_price_new - (record.website_price_new * 0.06)

            record.lkpp_govt_price = price

class ProductUoM(models.Model):
    _inherit = 'product.uom'

    lkpp_uom_id = fields.Char()
