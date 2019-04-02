# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.http import request


class Website(models.Model):
	_inherit = "website"

	@api.multi
	def _prepare_sale_order_values(self, partner, pricelist):
		vals = super(Website, self)._prepare_sale_order_values(partner, pricelist)
		if not vals.get('origin_url'):
			vals['origin_url'] = request.httprequest.url_root
		return vals


class SaleOrder(models.Model):
	_inherit = "sale.order"

	origin_url = fields.Char('URL Origin')

	@api.multi
	def get_access_action(self):
		self.ensure_one()
		res = super(SaleOrder, self).get_access_action()
		if res.get('url') and self.origin_url:
			res['url'] = "%s%s" % (self.origin_url, res.get('url'))
		return res


class EventRegistration(models.Model):
	_inherit = "event.registration"

	origin_url = fields.Char('URL Origin')

	@api.model
	def _prepare_attendee_values(self, registration):
		data = super(EventRegistration, self)._prepare_attendee_values(registration)
		if 'origin_url' not in res:
			data['origin_url'] = request.httprequest.url_root
		return data