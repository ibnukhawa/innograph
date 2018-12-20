# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime, date
from odoo.addons.amount_to_text_id.amount_to_text import Terbilang
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF, DEFAULT_SERVER_DATE_FORMAT as DF

class SaleOrder(models.Model):
	_inherit = "sale.order"

	quotation_number = fields.Char(help="keep quotation number when change into Sales Order")
	amount_text = fields.Char(compute='terbilang')
	valid_days = fields.Integer(compute='_get_valid_day')

	@api.model
	def create(self, vals):
		vals['name'] = self.env['ir.sequence'].with_context(force_company=vals['company_id']).next_by_code('inno.quotation') or _('New')
		return super(SaleOrder, self).create(vals)

	@api.multi
	def action_confirm(self):
		res = super(SaleOrder, self).action_confirm()
		for sale in self:
			if sale.state == 'sale':
				sale.quotation_number = sale.name
				sale.name = self.env['ir.sequence'].with_context(force_company=self.company_id.id).next_by_code('inno.sale.order') or self.name	

	def _get_contact_person(self):
		contact = False
		if self.partner_id:
			contact_src = self.partner_id.child_ids.filtered(lambda x:x.type == 'contact')
			if any(contact_src):
				contact = contact_src[0]
			else:
				contact = self.partner_id
		return contact

	@api.one
	def terbilang(self):
		self.amount_text = Terbilang(self.amount_total)

	def _get_valid_day(self):
		diff = 0
		if self.date_order and self.validity_date:
			date_order = datetime.strptime(self.date_order, DTF).date()
			year, month, day = self.validity_date.split('-')
			validity_date = date(int(year), int(month), int(day))
			delta = validity_date - date_order
			diff = delta.days
		self.valid_days = diff
