# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class MrpPartRequest(models.Model):
	_name = 'mrp.part.request'
	_description = 'Request Part for BoM'
	_order = 'date_scheduled desc'

	name = fields.Char(string="Reference")
	product_id = fields.Many2one('product.template', string="Product")
	bom_id = fields.Many2one('mrp.bom', string="Bill of Materials")
	location_src_id = fields.Many2one('stock.location', string="Source Location")
	location_dest_id = fields.Many2one('stock.location', string="Destination Location")
	date_scheduled = fields.Datetime(string="Scheduled Date")
	state = fields.Selection([('draft', 'Draft'),
							  ('confirm', 'Confirmed'),
							  ('cancel', 'Cancel'),
							  ('done', 'Done')], string="Status", default='draft')
	part_request_ids = fields.One2many('mrp.part.request.line', 'part_request_id', string="Material Request Line")
	warehouse_id = fields.Many2one('stock.warehouse', string="Warehouse")
	picking_count = fields.Integer(compute="compute_picking_count")
	production_id = fields.Many2one('mrp.production', string="Production")
	partner_id = fields.Many2one('res.partner', related='production_id.partner_id')
	company_id = fields.Many2one('res.company', string='Company', change_default=True,
        required=True, readonly=True, default=lambda self: self.env.user.company_id.id)

	@api.model
	def default_get(self, fields):
		res = super(MrpPartRequest, self).default_get(fields)
		warehouse_obj = self.env['stock.warehouse']
		warehouse = warehouse_obj.search([('id', '=', 1)], limit=1)
		if warehouse:
			res['warehouse_id'] = warehouse.id
			res['location_src_id'] = warehouse.lot_stock_id.id
		return res

	@api.multi
	@api.onchange('product_id')
	def onchange_product_template(self):
		for doc in self:
			product = doc.product_id
			if product:
				bom_ids = product.bom_ids.filtered(lambda x: x.active == True)
				if any(bom_ids):
					doc.bom_id = bom_ids[0].id

	@api.multi
	@api.onchange('warehouse_id')
	def onchange_warehouse_id(self):
		for doc in self:
			wh = doc.warehouse_id
			if wh:
				doc.location_src_id = wh.lot_stock_id.id

	@api.multi
	def action_confirm(self):
		picking_type_obj = self.env['stock.picking.type']
		for req in self:
			src_loc = req.location_src_id
			dst_loc = req.location_dest_id
			domain = [('warehouse_id', '=', req.warehouse_id.id), 
					  ('code', '=', 'internal')]
			picking_type = picking_type_obj.search(domain, limit=1)
			values = {
				'location_id': src_loc.id,
				'location_dest_id': dst_loc.id,
				'min_date': req.date_scheduled,
				'origin': req.name,
				'picking_type_id': picking_type.id
			}
			picking = self.env['stock.picking'].create(values)
			for line in req.part_request_ids:
				vals = {
					'product_id': line.product_id.id,
					'name': line.product_id.display_name,
					'product_uom_qty': line.quantity,
					'product_uom': line.uom_id.id,
					'location_id': src_loc.id,
					'location_dest_id': dst_loc.id,
				}
				move = self.env['stock.move'].create(vals)
				if move:
					picking.write({'move_lines': [(4, move.id)]})
					line.write({'move_id': move.id})
			picking.action_confirm()
			picking.action_assign()
		self.write({'state': 'confirm'})

	@api.multi
	def compute_picking_count(self):
		for req in self:
			moves = req.part_request_ids.mapped('move_id')
			picks = moves.mapped('picking_id')
			req.picking_count = len(picks)

	@api.multi
	def action_done(self):
		self.write({'state': 'done'})

	@api.multi
	def action_cancel(self):
		moves = self.mapped('part_request_ids').mapped('move_id')
		picks = moves.mapped('picking_id')
		done_picks = picks.filtered(lambda x: x.state == 'done')
		if len(done_picks) >= 1:
			raise UserError(_('You can not cancel request as some Internal Transfers have already done.'))
		else:
			picks.action_cancel()
		self.write({'state': 'cancel'})

	@api.multi
	def action_draft(self):
		self.write({'state': 'draft'})

	def action_fill_part_request_lines(self):
		if self.bom_id:
			part_line_obj = self.env['mrp.part.request.line']
			product_not_todo = self.env['product.product']
			if self.production_id:
				moves = self.production_id.move_raw_ids
				product_not_todo = moves.filtered(lambda x: x.state not in ['draft', 'waiting', 'confirmed']).mapped('product_id')
			for line in self.bom_id.bom_line_ids.filtered(lambda l: l.product_id.id not in product_not_todo.ids):
				vals = {
					'product_id': line.product_id.id,
					'description': line.product_id.display_name,
					'uom_id': line.product_uom_id.id,
					'quantity': line.product_qty,
					'item_size': line.item_size,
					'item_qty': line.item_qty
				}
				new_line = part_line_obj.create(vals)
				self.write({'part_request_ids': [(4, new_line.id)]})
		return True

	@api.model
	def create(self, vals):
		if not vals.get('name', False) or vals['name'] == _('New'):
			vals['name'] = self.env['ir.sequence'].next_by_code('mrp.part.request') or _('New')
		res = super(MrpPartRequest, self).create(vals)
		if vals.get('bom_id'):
			res.action_fill_part_request_lines()
		return res

	@api.multi
	def write(self, vals):
		if 'bom_id' in vals:
			self.part_request_ids = False
			self.action_fill_part_request_lines()
		return super(MrpPartRequest, self).write(vals)

	@api.multi
	def action_view_picking(self):
		moves = self.mapped('part_request_ids').mapped('move_id')
		pickings = moves.mapped('picking_id')
		action = self.env.ref('stock.action_picking_tree_all').read()[0]
		if len(pickings) > 1:
			action['domain'] = [('id', 'in', pickings.ids)]
		elif len(pickings) == 1:
			action['views'] = [(self.env.ref('stock.view_picking_form').id, 'form')]
			action['res_id'] = pickings.ids[0]
		else:
			action = {'type': 'ir.actions.act_window_close'}
		action['context'] = self.env.context
		return action



class MrpPartRequestLine(models.Model):
	_name = 'mrp.part.request.line'

	part_request_id = fields.Many2one('mrp.part.request', string="Material Request")
	product_id = fields.Many2one('product.product', string="Product")
	description = fields.Char()
	quantity = fields.Float()
	uom_id = fields.Many2one('product.uom', string="Unit of Measure")
	item_size = fields.Char()
	item_qty = fields.Integer()
	move_id = fields.Many2one('stock.move', string="Stock Move")