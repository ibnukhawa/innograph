# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime, date, timedelta
from odoo.addons.amount_to_text_id.amount_to_text import Terbilang
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF, DEFAULT_SERVER_DATE_FORMAT as DF

class SaleOrder(models.Model):
	_inherit = "sale.order"

	quotation_number = fields.Char(help="keep quotation number when change into Sales Order")
	amount_text = fields.Char(compute='terbilang')
	valid_days = fields.Integer(compute='_get_valid_day')
	date_planned = fields.Date(compute='_compute_date_planned')

	@api.multi
	def _compute_date_planned(self):
		for sale in self:
			if sale.order_line:
				lead_list = sale.order_line.mapped('customer_lead')
				min_lead = min(lead_list)
				sale.date_planned = datetime.strptime(sale.date_order, DTF) + timedelta(days=min_lead)

	@api.model
	def create(self, vals):
		if not vals.get('company_id'):
			vals['company_id'] = self.env.user.company_id.id
		vals['name'] = self.env['ir.sequence'].with_context(force_company=vals['company_id']).next_by_code('inno.quotation') or _('New')
		return super(SaleOrder, self).create(vals)

	@api.multi
	def action_confirm(self):
		res = super(SaleOrder, self).action_confirm()
		for sale in self:
			if sale.state == 'sale':
				sale.quotation_number = sale.name
				sale.name = self.env['ir.sequence'].with_context(force_company=sale.company_id.id).next_by_code('inno.sale.order') or sale.name
		return res

	@api.multi
	def _get_contact_person(self):
		for sale in self:
			contact = False
			if sale.partner_id:
				contact_src = sale.partner_id.child_ids.filtered(lambda x:x.type == 'contact')
				if any(contact_src):
					contact = contact_src[0]
				else:
					contact = sale.partner_id
			return contact

	@api.one
	def terbilang(self):
		self.amount_text = Terbilang(self.amount_total)

	@api.multi
	def _get_valid_day(self):
		for sale in self:
			diff = 0
			if sale.date_order and sale.validity_date:
				date_order = datetime.strptime(sale.date_order, DTF).date()
				year, month, day = sale.validity_date.split('-')
				validity_date = date(int(year), int(month), int(day))
				delta = validity_date - date_order
				diff = delta.days
			sale.valid_days = diff
