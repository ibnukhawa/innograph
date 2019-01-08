# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime


class CRMLead(models.Model):
	_inherit = "crm.lead"

	@api.multi
	@api.onchange('lead_product_ids', 'lead_product_ids.price_unit')
	def _onchange_products_price_unit(self):
		for lead in self:
			total = 0
			for line in lead.lead_product_ids:
				total += (line.price_unit * line.qty)
			lead.planned_revenue = total


	@api.multi
	def write(self, vals):
		if 'team_id' in vals:
			stage_ids = self.env['crm.stage'].search([('team_id', '=', vals.get('team_id'))])
			for stage in stage_ids:
				vals['stage_id'] = stage.id
				break
		return super(CRMLead, self).write(vals)




	