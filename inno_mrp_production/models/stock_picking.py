# -*- coding: utf-8 -*-
from odoo import fields, models


class StockPicking(models.Model):
	_inherit = "stock.picking"

	request_material_id = fields.Many2one('mrp.part.request', string="Material Request")