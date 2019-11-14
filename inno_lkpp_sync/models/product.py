# -*- coding: utf-8 -*-
from odoo import fields, models, api
import odoo.addons.decimal_precision as dp

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    unspsc = fields.Char(string='UNSPSC', size=8)
    active_product = fields.Boolean()
    local_product = fields.Boolean()
    tkdn_product = fields.Boolean()
    valid_date = fields.Date(string='Valid Until')
    specification = fields.Text()

    lkpp_category_id = fields.Char(string='Category')
    lkpp_manufacturer_id = fields.Char(string='Manufacturer')
    lkpp_uom_id = fields.Char(string='Unit Pengukuran')

    # lkpp_sell_price = fields.Float(string='Sell Price')

    lkpp_govt_price = fields.Float(string='Goverment Price',compute='_computed_price_goverment')
    website_price = fields.Float(string='Website Price',compute='_computed_website_price')
    
    #restore sale price field
    list_price = fields.Float(
        'Sale Price', default=1.0,
        digits=dp.get_precision('Product Price'),
        help="Base price to compute the customer price. Sometimes called the catalog price.")

    deskripsi_lengkap = fields.Text(string="Deskripsi Lengkap")
    deskripsi_singkat = fields.Text(string="Deskripsi Singkat")

    # @api.depends("website_price_new")
    # def _computed_price_website(self):
    #     for record in self:
    #         price = record.website_price_new + (record.website_price_new * 0.1)

    #         record.list_price = price

    def _computed_website_price(self):
        for record in self:
            print (record.company_id.default_website_pricelist_id.name)
            company = record.company_id
            website_price = 0  
            if not company:
                company = self.env['res.users'].browse(self.env.uid).company_id
            website_pricelist = company.default_website_pricelist_id
            if website_pricelist:
                website_price = (record.with_context(pricelist=website_pricelist.id).price)
            record.website_price = website_price

    def _computed_price_goverment(self):
        for record in self:
            print (record.company_id.lkpp_government_pricelist_id.name)
            company = record.company_id
            lkpp_price = 0  
            if not company:
                company = self.env['res.users'].browse(self.env.uid).company_id
            lkpp_pricelist = company.lkpp_government_pricelist_id
            if lkpp_pricelist:
                lkpp_price = (record.with_context(pricelist=lkpp_pricelist.id).price)
            record.lkpp_govt_price = lkpp_price

class ProductUoM(models.Model):
    _inherit = 'product.uom'

    lkpp_uom_id = fields.Char()
