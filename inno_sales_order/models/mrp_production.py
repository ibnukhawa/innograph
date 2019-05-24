# -*- coding: utf-8 -*-
from odoo import models, fields, api


class MrpProduction(models.Model):
	_inherit = 'mrp.production'

	@api.multi
	def write(self, vals):
		res = super(MrpProduction, self).write(vals)
		if 'name' in vals:
			if self.sale_id:
				for line in self.sale_id.order_line:
					if line.product_id.id == self.product_id.id:
						line.production_no = vals.get('name')
		return res