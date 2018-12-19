# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime


class SaleOrder(models.Model):
	_inherit = "sale.order"

	def _get_contact_person(self):
		contact = False
		if self.partner_id:
			contact_src = self.partner_id.child_ids.filtered(lambda x:x.type == 'contact')
			if any(contact_src):
				contact = contact_src[0]
			else:
				contact = self.partner_id
		return contact
				




	