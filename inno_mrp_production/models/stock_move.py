# -*- coding: utf-8 -*-
from odoo import fields, models


class StockMove(models.Model):
	_inherit = "stock.move"

	qty_initial = fields.Float(string="Initial Qty")