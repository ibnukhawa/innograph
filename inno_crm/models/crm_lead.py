# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime


class CRMLead(models.Model):
	_inherit = "crm.lead"

	stage_id = fields.Many2one('crm.stage', string='Stage', track_visibility='onchange', index=True, 
		group_expand='_read_group_stage_ids', default=lambda self: self._default_stage_id())

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
			stage_ids = self.env['crm.stage'].search([])
			stage_ids = stage_ids.filtered(lambda x:vals.get('team_id') in x.team_ids._ids)
			for stage in stage_ids.sorted('probability'):
				vals['stage_id'] = stage.id
				break
		if 'probability' in vals:
			prob = vals.get('probability')
			stage_id = self.env['crm.stage'].search([('probability', '>=', prob)], order='probability', limit=1)
			if stage_id:
				vals['stage_id'] = stage_id.id
		return super(CRMLead, self).write(vals)
	