# -*- coding: utf-8 -*-
from odoo import models, fields, api


class MrpBom(models.Model):
	_inherit = "mrp.bom"

	new_bom_id = fields.Many2one('mrp.bom', "New Bill of Materials")
	old_bom_id = fields.Many2one('mrp.bom', "Old Bill of Materials")

	@api.multi
	def apply_new_version(self):
		self.write({'active': True})
		self.mapped('old_bom_id').write({'active': False})