# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class ResPartner(models.Model):
	_inherit = "res.partner"

	is_division_head = fields.Boolean(string="Division Head", default=False)