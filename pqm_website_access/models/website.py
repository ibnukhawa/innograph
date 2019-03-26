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