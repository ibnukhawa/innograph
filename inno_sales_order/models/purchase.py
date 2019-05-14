# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class PurchaseOrder(models.Model):
	_inherit = "purchase.order"

	count_so = fields.Integer(compute="_compute_so", string="SO Count")

	@api.multi
	def _compute_so(self):
		for purchase in self:
			sales = purchase.order_line.mapped('sale_order_id')
			purchase.count_so = len(sales)

	@api.multi
	def action_view_sales(self):
		sales = self.mapped('order_line').mapped('sale_order_id')
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