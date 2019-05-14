# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class MrpProduction(models.Model):
	_inherit = 'mrp.production'


	def action_create_bom_revision(self):
		bom_revise = self.env['mrp.bom.revision']
		bom_revise_src = bom_revise.search([('bom_id', '=', self.bom_id.id), 
											('state', 'not in', ['done'])])
		if bom_revise_src:
			raise UserError(_("The same Bill of Material is already in revision process. \n \
							   Please finish current revision before create another one."))

		ctx = self.env.context.copy()
		ctx['default_product_tmpl_id'] = self.product_id.product_tmpl_id.id
		ctx['default_bom_id'] = self.bom_id.id
		ctx['default_name'] = 'Revise BoM:%s' % self.product_id.display_name
		
		action = self.env.ref('inno_mrp_bom_versioning.action_mrp_bom_revision').read()[0]
		action['views'] = [(self.env.ref('inno_mrp_bom_versioning.mrp_bom_revision_form_view').id, 'form')]
		action['context'] = ctx
		return action