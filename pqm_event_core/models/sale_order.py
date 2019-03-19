# -*- coding:utf-8 -*-
from odoo import models, fields, api, tools
from datetime import datetime

class SaleOrder(models.Model):
	_inherit = "sale.order"

	@api.multi
	def _website_product_id_change(self, order_id, product_id, qty=0):
		order = self.env['sale.order'].sudo().browse(order_id)
		values = super(SaleOrder, self)._website_product_id_change(order_id, product_id, qty=qty)
		
		if values.get('event_ticket_id', False) and values.get('event_id', False):
			name = values.get('name', '')
			event = values.get('event_id')
			ticket = values.get('event_ticket_id')
			domain = [('sale_order_id', '=', order_id), 
					  ('event_id', '=', event), 
					  ('event_ticket_id', '=', ticket)]
			registrations = self.env['event.registration'].sudo().search(domain)
			for reg in registrations:
				name = "%s\n - %s" % (name, reg.name)
			values['name'] = name
		return values