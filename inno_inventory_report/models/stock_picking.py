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
		return self.env['report'].get_action(self, 'inno_inventory_report.delivery_order_report')

	@api.multi
	def print_bpb(self):
		return self.env['report'].get_action(self, 'inno_inventory_report.delivery_order_report')

