# -*- coding: utf-8 -*-
""" Import """
from odoo import models, api


class StockPicking(models.Model):
	_inherit = 'stock.picking'

	@api.multi
	def print_surat_jalan(self):
		return self.env['report'].get_action(self, 'inno_inventory_report.delivery_slip_report')

	@api.multi
	def print_bbk(self):
		self.ensure_one()
		report = False
		if self.request_material_id:
			report = self.request_material_id.env['report'].get_action(self.request_material_id, 'inno_mrp_production.material_request_report')
		else:
			report = self.env['report'].get_action(self, 'inno_inventory_report.delivery_order_report')
		return report

	@api.multi
	def print_bpb(self):
		return self.env['report'].get_action(self, 'inno_inventory_report.delivery_order_report')

