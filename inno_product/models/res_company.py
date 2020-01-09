# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class ResCompany(models.Model):
	_inherit = 'res.company'

	default_finished_product_location = fields.Many2one('stock.location')


class StockSettings(models.TransientModel):
    _inherit = 'stock.config.settings'

    default_finished_product_location = fields.Many2one('stock.location', "Finished Product Location")


    @api.onchange('default_finished_product_location')
    def onchange_default_finished_product_location(self):
    	if self.default_finished_product_location and self.company_id:
    		self.company_id.write({'default_finished_product_location': self.default_finished_product_location.id})