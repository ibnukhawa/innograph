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
		for product in self:
			finished_loc = product.get_finished_good_location()
			product.qty_ready = product.with_context(location=finished_loc).qty_available
	
	@api.multi
	def action_open_finished_quants(self):
		whfg_loc = self.get_finished_good_location()
		action = self.env.ref('stock.product_open_quants').read()[0]
		domain = [
			('product_id', 'in', self.ids), 
			('location_id', 'in', whfg_loc)
		]
		action['domain'] = domain
		action['context'] = {'search_default_locationgroup': 0, 'search_default_internal_loc': 0}
		return action
		
	def get_finished_good_location(self):
		res = self.env.ref('stock.stock_location_stock')
		location_obj = self.env['stock.location']
		whfg_loc = location_obj.search([('name', '=', 'WHFG'), ('usage', '=', 'view')], limit=1)
		if whfg_loc:
			res = location_obj.search([('location_id', '=', whfg_loc.id), ('usage', '=', 'internal')])
		return res.ids