# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class ProcurementOrder(models.Model):
	""" Inherit Procurement Order """
	_inherit = 'procurement.order'


	@api.multi
	def run(self, autocommit=False):
		"""
			Inherit Run Procurement to set SO on Purchase Order Line that created when Confirming PO
			Even PO not created when Confirm SO, it will set when Run Procuement Order related to it
		"""
		res = super(ProcurementOrder, self).run(autocommit)
		for proc in self:
			po_line = proc.purchase_line_id
			group_id = proc.group_id
			if po_line and group_id and proc.state in ('running', 'done'):
				sale_src = self.env['sale.order'].search([('procurement_group_id', '=', group_id.id)], limit=1)
				if sale_src:
					line = sale_src.order_line.filtered(lambda l: l.product_id.id == po_line.product_id.id)
					proc.purchase_line_id.write({
						'sale_order_id': sale_src.id,
						'account_analytic_id': sale_src.related_project_id.id,
						'analytic_tag_ids': [(6, 0, line.analytic_tag_ids and line.analytic_tag_ids.ids or [])]	
					})
		return res
