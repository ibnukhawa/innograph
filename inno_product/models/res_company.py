# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class ResCompany(models.Model):
	_inherit = 'res.company'

	default_finished_product_location = fields.Many2one('stock.location')

