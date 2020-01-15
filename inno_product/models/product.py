# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.addons import decimal_precision as dp
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

	qty_ready = fields.Float('Quantity Ready to Ship', compute='_compute_qty_ready', 
		digits=dp.get_precision('Product Unit of Measure'))

	def _compute_qty_ready(self):
		whfg_loc = self.get_finished_good_location()
		for template in self:
			qty = 0
			for product in template.product_variant_ids:
				qty += product.with_context(location=whfg_loc).qty_available
			template.qty_ready = qty

	@api.multi
	def action_open_finished_quants(self):
		whfg_loc = self.get_finished_good_location()
		action = self.env.ref('stock.product_open_quants').read()[0]
		domain = [
			('product_id', 'in', self.mapped('product_variant_ids').ids), 
			('location_id', '=', whfg_loc)
		]
		action['domain'] = domain
		action['context'] = {'search_default_locationgroup': 0, 'search_default_internal_loc': 0}
		return action

	def get_finished_good_location(self):
		company_id = self.env.user.company_id
		location = company_id.default_finished_product_location or self.env.ref('stock.stock_location_stock')
		return location and location.id or False



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

	qty_ready = fields.Float('Quantity Ready to Ship', compute='_compute_qty_ready', 
		digits=dp.get_precision('Product Unit of Measure'))

	@api.depends('stock_quant_ids', 'stock_move_ids')
	def _compute_qty_ready(self):
		whfg_loc = self.get_finished_good_location()
		for product in self:
			product.qty_ready = product.with_context(location=whfg_loc).qty_available
	
	@api.multi
	def action_open_finished_quants(self):
		whfg_loc = self.get_finished_good_location()
		action = self.env.ref('stock.product_open_quants').read()[0]
		domain = [
			('product_id', 'in', self.ids), 
			('location_id', '=', whfg_loc)
		]
		action['domain'] = domain
		action['context'] = {'search_default_locationgroup': 0, 'search_default_internal_loc': 0}
		return action
		
	def get_finished_good_location(self):
		company_id = self.env.user.company_id
		location = company_id.default_finished_product_location or self.env.ref('stock.stock_location_stock')
		return location and location.id or False