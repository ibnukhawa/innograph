# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class ProductCategory(models.Model):
	_inherit = "product.category"

	category_image = fields.Binary(string="Category Image",
								   help="Image for Category Product,",
								   attachment=True)
