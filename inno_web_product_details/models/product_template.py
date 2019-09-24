# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ProductTemplate(models.Model):
	_inherit = 'product.template'

	short_description = fields.Html(string='Deskripsi singkat')
	product_detail = fields.Html(string='Detail Produk')
	installation_instructions = fields.Html(string='Petunjuk Pemasangan')
	product_gallery = fields.Html(string='Galery Produk')