# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ProductTemplate(models.Model):
	_inherit = 'product.template'

	counter_view = fields.Integer(string='Viewer')
	sold_product = fields.Integer(string='Product Sold')
