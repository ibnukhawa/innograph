# -*- coding: utf-8 -*-
from odoo import models, fields, api


class StockPicking(models.Model):
	_inherit = 'stock.picking'

	sale_order_id = fields.Many2one('sale.order', string="Sale Order")
	
	@api.multi
	def action_open_sales(self):
		sales = self.mapped('sale_id')
		action = self.env.ref('sale_approval.action_orders_extends').read()[0]
		if len(sales) > 1:
			action['domain'] = [('id', 'in', sales.ids)]
		elif len(sales) == 1:
			action['views'] = [(self.env.ref('sale.view_order_form').id, 'form')]
			action['res_id'] = sales.ids[0]
		else:
			action = {'type': 'ir.actions.act_window_close'}
		action['context'] = self.env.context
		return action

	@api.model
	def create(self, vals):
		if 'sale_order_id' in vals and 'group_id' not in vals:
			sale = self.env['sale.order'].search([('id', '=', vals.get('sale_order_id'))])
			vals['group_id'] = sale.procurement_group_id.id
		return super(StockPicking, self).create(vals)

	@api.multi
	def write(self, vals):
		if 'sale_order_id' in vals:
			sale = self.env['sale.order'].search([('id', '=', vals.get('sale_order_id'))])
			vals['group_id'] = sale.procurement_group_id.id
		return super(StockPicking, self).write(vals)
	
	@api.one
	@api.depends('move_lines.procurement_id.sale_line_id.order_id')
	def _compute_sale_id(self):
		res = super(StockPicking, self)._compute_sale_id()
		if self.sale_order_id and not self.sale_id:
			self.sale_id = self.sale_order_id.id 
		return res
