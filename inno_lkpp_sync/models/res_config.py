# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    lkpp_category_key = fields.Char(string='Category')
    lkpp_uom_key = fields.Char(string='Units of Measure')
    lkpp_manufacture_key = fields.Char(string='Manufacturer')
    lkpp_currency_key = fields.Char(string='Currency')
    lkpp_secretkey = fields.Char(string='Secret Key')

    @api.model
    def get_default_lkpp_api_key(self, fields):
        return {
            'lkpp_category_key': self.env['ir.config_parameter'].sudo().get_param('lkpp.category_key', default=''),
            'lkpp_uom_key': self.env['ir.config_parameter'].sudo().get_param('lkpp.uom_key', default=''),
            'lkpp_manufacture_key': self.env['ir.config_parameter'].sudo().get_param('lkpp.manufacture_key', default=''),
            'lkpp_currency_key': self.env['ir.config_parameter'].sudo().get_param('lkpp.currency_key', default=''),
            'lkpp_secretkey': self.env['ir.config_parameter'].sudo().get_param('lkpp.secretkey', default='')
        }

    @api.multi
    def set_lkpp_api_key(self):
        self.env['ir.config_parameter'].sudo().set_param('lkpp.category_key', (self.lkpp_category_key or '').strip(), groups=['base.group_system'])
        self.env['ir.config_parameter'].sudo().set_param('lkpp.uom_key', (self.lkpp_uom_key or '').strip(), groups=['base.group_system'])
        self.env['ir.config_parameter'].sudo().set_param('lkpp.manufacture_key', (self.lkpp_manufacture_key or '').strip(), groups=['base.group_system'])
        self.env['ir.config_parameter'].sudo().set_param('lkpp.currency_key', (self.lkpp_currency_key or '').strip(), groups=['base.group_system'])
        self.env['ir.config_parameter'].sudo().set_param('lkpp.secretkey', (self.lkpp_secretkey or '').strip(), groups=['base.group_system'])
