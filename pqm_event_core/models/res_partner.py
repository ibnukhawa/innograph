# -*- coding:utf-8 -*-
from odoo import models, fields, api


class ResPartner(models.Model):
	_inherit = 'res.partner'

	is_facilitator = fields.Boolean("Facilitator", default=False)
	registered_event_ids = fields.One2many('event.registration', 'contact_id', string="Event Register")
	url_facilitator = fields.Char("Facilitator URL")
