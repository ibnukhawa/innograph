# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime, date, timedelta
from odoo.addons.amount_to_text_id.amount_to_text import Terbilang
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF, DEFAULT_SERVER_DATE_FORMAT as DF

class SaleOrder(models.Model):
	_inherit = "sale.order"

	quotation_number = fields.Char(help="keep quotation number when change into Sales Order")
	amount_text = fields.Char(compute='terbilang')
	valid_days = fields.Integer(compute='_get_valid_day')
	date_planned = fields.Date(compute='_compute_date_planned')
	count_po = fields.Integer(compute="_compute_po", string="PO Count")
	count_wo = fields.Integer(compute="_compute_wo", string="WO Count")
	count_mo = fields.Integer(compute="_compute_mo", string="MO Count")

	@api.multi
	def _compute_date_planned(self):
		for sale in self:
			if sale.order_line:
				lead_list = sale.order_line.mapped('customer_lead')
				min_lead = min(lead_list)
				sale.date_planned = datetime.strptime(sale.date_order, DTF) + timedelta(days=min_lead)

	@api.model
	def create(self, vals):
		if not vals.get('company_id'):
			vals['company_id'] = self.env.user.company_id.id
		vals['name'] = self.env['ir.sequence'].with_context(force_company=vals['company_id']).next_by_code('inno.quotation') or _('New')
		return super(SaleOrder, self).create(vals)

	@api.multi
	def action_confirm(self):
		for sale in self:
			so_name = sale.name.split('-')
			if so_name[0] == 'SO':
				continue
			sale.quotation_number = sale.name
			sale.name = self.env['ir.sequence'].with_context(force_company=sale.company_id.id).next_by_code('inno.sale.order') or sale.name
		res = super(SaleOrder, self).action_confirm()
		# Store new created MO to Order Line or Change MO Name from stored in Order Line
		for order in self:
			mo_src = self.env['mrp.production'].search([('sale_id', '=', order.id)])
			line_mo = False
			if mo_src:
				for line in order.order_line:
					# For MO
					if not line_mo:
						line_mo = mo_src.filtered(lambda x: x.product_id.id == line.product_id.id and x.state != 'cancel')
					else:
						line_mo = mo_src.filtered(lambda x: x.product_id.id == line.product_id.id and x.state != 'cancel' and x.id!=line_mo.id)
					if line_mo:
						if not line.production_no:
							line.production_no = line_mo[0].name
						else:
							line_mo[0].name = line.production_no
		return res

	@api.multi
	def _get_contact_person(self):
		for sale in self:
			contact = False
			if sale.partner_id:
				contact_src = sale.partner_id.child_ids.filtered(lambda x:x.type == 'contact')
				if any(contact_src):
					contact = contact_src[0]
				else:
					contact = sale.partner_id
			return contact

	@api.one
	def terbilang(self):
		self.amount_text = Terbilang(self.amount_total)

	@api.multi
	def _get_valid_day(self):
		for sale in self:
			diff = 0
			if sale.date_order and sale.validity_date:
				date_order = datetime.strptime(sale.date_order, DTF).date()
				year, month, day = sale.validity_date.split('-')
				validity_date = date(int(year), int(month), int(day))
				delta = validity_date - date_order
				diff = delta.days
			sale.valid_days = diff


	@api.multi
	def _compute_po(self):
		for sale in self:
			po_lines = self.env['purchase.order.line'].search([('sale_order_id', '=', sale.id)])
			purchase = po_lines.mapped('order_id')
			sale.count_po = len(purchase)

	@api.multi
	def _compute_wo(self):
		for sale in self:
			mo_src = self.env['mrp.production'].search([('sale_id', '=', sale.id)])
			workorders = mo_src.mapped('workorder_ids')
			sale.count_wo = len(workorders)

	@api.multi
	def _compute_mo(self):
		for sale in self:
			mo_src = self.env['mrp.production'].search([('sale_id', '=', sale.id)])
			sale.count_mo = len(mo_src)

	@api.multi
	def action_view_po(self):
		sale_ids = self.mapped('id')
		po_lines = self.env['purchase.order.line'].search([('sale_order_id', 'in', sale_ids)])
		purchases = po_lines.mapped('order_id')
		action = self.env.ref('purchase.purchase_form_action').read()[0]
		if len(purchases) > 1:
			action['domain'] = [('id', 'in', purchases.ids)]
		elif len(purchases) == 1:
			action['views'] = [(self.env.ref('purchase.purchase_order_form').id, 'form')]
			action['res_id'] = purchases.ids[0]
		else:
			action = {'type': 'ir.actions.act_window_close'}
		action['context'] = self.env.context
		return action

	@api.multi
	def action_view_mo(self):
		sale_ids = self.mapped('id')
		mo_src = self.env['mrp.production'].search([('sale_id', 'in', sale_ids)])
		action = self.env.ref('mrp.mrp_production_action').read()[0]
		if len(mo_src) > 1:
			action['domain'] = [('id', 'in', mo_src.ids)]
		elif len(mo_src) == 1:
			action['views'] = [(self.env.ref('mrp.mrp_production_form_view').id, 'form')]
			action['res_id'] = mo_src.ids[0]
		else:
			action = {'type': 'ir.actions.act_window_close'}
		action['context'] = self.env.context
		return action

	@api.multi
	def action_view_wo(self):
		sale_ids = self.mapped('id')
		mo_src = self.env['mrp.production'].search([('sale_id', 'in', sale_ids)])
		workorders = mo_src.mapped('workorder_ids')
		action = self.env.ref('mrp.mrp_workorder_todo').read()[0]
		if len(workorders) > 1:
			action['domain'] = [('id', 'in', workorders.ids)]
		elif len(workorders) == 1:
			action['views'] = [(self.env.ref('mrp.mrp_production_workcenter_tree_view_inherit').id, 'form')]
			action['res_id'] = workorders.ids[0]
		else:
			action = {'type': 'ir.actions.act_window_close'}
		action['context'] = self.env.context
		return action

	@api.model
	def default_get(self, fields):
		""" Set Default Warehouse to Finished Goods (WHFG) """
		res = super(SaleOrder, self).default_get(fields)
		warehouse_obj = self.env['stock.warehouse']
		warehouse = warehouse_obj.search([('code', '=', 'WHFG')], limit=1)
		if warehouse:
			res['warehouse_id'] = warehouse.id
		return res

	@api.multi
	def action_cancel(self):
		""" Cancel SO will delete MO if MO not In Progress/Done """
		for order in self:
			mo_src = self.env['mrp.production'].search([('sale_id', '=', order.id)])
			if len(mo_src.filtered(lambda x: x.state in ['progress', 'done'])) > 0:
				raise UserError(_("You can not cancel this order because there is related "\
					"Manufacturing Order with state already In Progress / Done."))
			mo_src = self.env['mrp.production'].search([('sale_id', '=', order.id)])
			to_remove_mo = mo_src.filtered(lambda x: x.state in ['draft', 'confirmed', 'planned'])
			to_remove_mo.action_cancel()
			# to_remove_mo.mapped('workorder_ids').unlink()
			mo_src.filtered(lambda x: x.state == 'cancel').unlink()
		return super(SaleOrder, self).action_cancel()


class SaleOrderLine(models.Model):
	_inherit = 'sale.order.line'

	production_no = fields.Char(string="Number Production")