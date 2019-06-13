# -*- coding: utf-8 -*-
from odoo import models, fields, api


class StockPicking(models.Model):
	_inherit = 'stock.picking'

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