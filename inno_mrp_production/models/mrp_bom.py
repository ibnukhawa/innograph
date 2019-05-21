# -*- coding: utf-8 -*-
from odoo import api, fields, models


class MrpBomLine(models.Model):
	_inherit = 'mrp.bom.line'

	item_size = fields.Char()
	item_qty = fields.Integer()