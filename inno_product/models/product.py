# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ProductTemplate(models.Model):
	_inherit = "product.template"

	inv_part_type = fields.Selection([('finished_goods', 'Finished Goods'),
									  ('raw_material', 'Raw Material'),
									  ('subsidiary_material', 'Subsidiary Material'),
									  ('in_process', 'Work In Process'),
									  ('other', 'Other material'),
									  ('service', 'Service')
									 ], string="Inventory Part Type")



class ProductProduct(models.Model):
	_inherit = "product.product"

	inv_part_type = fields.Selection([('finished_goods', 'Finished Goods'),
									  ('raw_material', 'Raw Material'),
									  ('subsidiary_material', 'Subsidiary Material'),
									  ('in_process', 'Work In Process'),
									  ('other', 'Other material'),
									  ('service', 'Service')
									 ], string="Inventory Part Type",
									 related="product_tmpl_id.inv_part_type")
