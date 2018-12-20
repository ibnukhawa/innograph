# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime
from odoo.addons.amount_to_text_id.amount_to_text import Terbilang

class SaleOrder(models.Model):
	_inherit = "sale.order"

	amount_text = fields.Char(compute='terbilang')

	@api.model
	def create(self, vals):
		vals['name'] = self.env['ir.sequence'].with_context(force_company=vals['company_id']).next_by_code('inno.quotation') or _('New')
		return super(SaleOrder, self).create(vals)

	@api.multi
	def action_confirm(self):
		res = super(SaleOrder, self).action_confirm()
		if self.state == 'sale':
			self.name = self.env['ir.sequence'].with_context(force_company=self.company_id.id).next_by_code('inno.sale.order') or self.name	

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
