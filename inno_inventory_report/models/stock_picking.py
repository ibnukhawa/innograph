# -*- coding: utf-8 -*-
""" Import """
from odoo import models, api, fields


class StockPicking(models.Model):
	_inherit = 'stock.picking'

	show_bbk = fields.Boolean(compute="_compute_show_bbk", default=False)
	show_spb = fields.Boolean(compute="_compute_show_bbk", default=False)

	@api.multi
	@api.depends('state', 'picking_type_code', 'location_dest_id')
	def _compute_show_bbk(self):
		for pick in self.filtered(lambda x: x.picking_type_code == 'internal' \
				and x.state in ['assigned', 'partially_available', 'done']):
			picking_type = pick.picking_type_id
			if picking_type.default_location_dest_id and picking_type.default_location_dest_id.usage == 'transit' \
				or picking_type.default_location_src_id and picking_type.default_location_src_id.usage == 'transit':
				pick.show_spb = True
			else:
				pick.show_bbk = True

	@api.multi
	def print_surat_jalan(self):
		return self.env['report'].get_action(self, 'inno_inventory_report.delivery_slip_report')

	@api.multi
	def print_bbk(self):
		self.ensure_one()
		report = False
		if self.request_material_id:
			self = self.request_material_id
			report = self.env['report'].get_action(self, 'inno_mrp_production.material_request_report')
		else:
			report = self.env['report'].get_action(self, 'inno_inventory_report.delivery_order_report')
		return report

	@api.multi
	def print_bpb(self):
		return self.env['report'].get_action(self, 'inno_inventory_report.delivery_order_report')

	@api.multi
	def print_spb(self):
		return self.env['report'].get_action(self, 'inno_inventory_report.delivery_order_report')

