# -*- coding: utf-8 -*-
from odoo import models, fields, api, _, tools
from odoo.exceptions import UserError


class MrpBomRevision(models.Model):
	_name = "mrp.bom.revision"
	_description = 'BOM Revision'
	_inherit = ['mail.thread', 'ir.needaction_mixin']

	name = fields.Char(string="Short Summary")
	product_tmpl_id = fields.Many2one('product.template', track_visibility='always', 
		string="Product", domain=[('bom_ids', '!=', False)])
	bom_id = fields.Many2one('mrp.bom', track_visibility='always', string="Bill of Materials")
	new_bom_id = fields.Many2one('mrp.bom', track_visibility='always', string="New Bill of Materials")
	responsible_id = fields.Many2one('res.users', track_visibility='always', string="Responsible", default=lambda self: self.env.user)
	approver_id = fields.Many2one('res.users', track_visibility='always', string="Approver")
	state = fields.Selection([('draft', 'Draft'),
							  ('submit', 'Submitted'),
							  ('approve', 'Approved'),
							  ('reject', 'Rejected'),
							  ('cancel', 'Cancelled'),
							  ('done', 'Done')
							 ], track_visibility='always', string="Status", default="draft")
	note = fields.Text()
	bom_change_ids = fields.One2many('mrp.bom.revision.change', 'bom_revision_id', 
		string="Bom Change Lines", compute='_compute_bom_change_ids', store=True)
	revision_count = fields.Integer(compute="compute_revision_count")
	is_responsible = fields.Boolean(compute="_check_responsible")
	is_approver = fields.Boolean(compute="_check_approver")

	@api.multi
	@api.onchange('product_tmpl_id')
	def onchange_product_template(self):
		for doc in self:
			product = doc.product_tmpl_id
			if product:
				bom_ids = product.bom_ids.filtered(lambda x: x.active == True)
				if any(bom_ids):
					doc.bom_id = bom_ids[0].id

	@api.multi
	def action_view_revision(self):
		self.ensure_one()
		if not self.new_bom_id:
			new_bom = self.bom_id.copy()
			new_bom.write({
				'active': False, 
				'old_bom_id': self.bom_id.id
			})
			self.bom_id.write({'new_bom_id': new_bom.id})
			self.new_bom_id = new_bom.id
		return {
			'name': _("New Bill of Materials"),
			'type': 'ir.actions.act_window',
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'mrp.bom',
			'target': 'current',
			'res_id': self.new_bom_id.id,
		}

	@api.one
	@api.depends('bom_id.bom_line_ids', 'new_bom_id.bom_line_ids')
	def _compute_bom_change_ids(self):
		new_bom_commands = []
		old_bom_lines = dict(((line.product_id, line.product_uom_id, tuple(line.attribute_value_ids.ids),), line) for line in self.bom_id.bom_line_ids)
		if self.new_bom_id and self.bom_id:
			for line in self.new_bom_id.bom_line_ids:
				key = (line.product_id, line.product_uom_id, tuple(line.attribute_value_ids.ids),)
				old_line = old_bom_lines.pop(key, None)
				if old_line and tools.float_compare(old_line.product_qty, line.product_qty, line.product_uom_id.rounding) != 0:
					new_bom_commands += [(0, 0, {
						'change_type': 'update',
						'product_id': line.product_id.id,
						'product_uom_id': line.product_uom_id.id,
						'new_product_qty': line.product_qty,
						'old_product_qty': old_line.product_qty})]
				elif not old_line:
					new_bom_commands += [(0, 0, {
						'change_type': 'add',
						'product_id': line.product_id.id,
						'product_uom_id': line.product_uom_id.id,
						'new_product_qty': line.product_qty
					})]
			for key, old_line in old_bom_lines.iteritems():
				new_bom_commands += [(0, 0, {
					'change_type': 'remove',
					'product_id': old_line.product_id.id,
					'product_uom_id': old_line.product_uom_id.id,
					'old_product_qty': old_line.product_qty,
				})]
		self.bom_change_ids = new_bom_commands

	def _check_responsible(self):
		if self.responsible_id.id == self.env.user.id:
			self.is_responsible = True

	def _check_approver(self):
		if self.approver_id.id == self.env.user.id:
			self.is_approver = True

	def compute_revision_count(self):
		count = 0
		old_bom = self.bom_id.old_bom_id
		while old_bom:
			count += 1
			old_bom = old_bom.old_bom_id
		self.revision_count = count+1

	@api.multi
	def action_submit(self):
		for doc in self:
			if self.env.user != doc.responsible_id:
				raise UserError(_('You can not Submit this document.'))
			doc.write({'state': 'submit'})

	@api.multi
	def action_approve(self):
		for doc in self:
			doc.write({'state': 'approve'})

	@api.multi
	def action_reject(self):
		for doc in self:
			doc.write({'state': 'reject'})

	@api.multi
	def action_cancel(self):
		for doc in self:
			doc.write({'state': 'cancel'})

	@api.multi
	def action_draft(self):
		for doc in self:
			doc.write({'state': 'draft'})

	@api.multi
	def action_apply(self):
		self.mapped('new_bom_id').apply_new_version()
		self.write({'state': 'done'})

class MrpBomRevisionChange(models.Model):
	_name = "mrp.bom.revision.change"

	new_product_qty = fields.Float(string="New Qty")
	old_product_qty = fields.Float(string="Current Qty")
	upd_product_qty = fields.Float(string="Quantity", compute="compute_qty")
	bom_revision_id = fields.Many2one('mrp.bom.revision', string="Bom Revision")
	old_uom_id = fields.Many2one('product.uom', related="product_id.uom_id", string="Current Uom")
	new_uom_id = fields.Many2one('product.uom', related="product_id.uom_id", string="New Uom")
	product_id = fields.Many2one('product.product', string="Product")
	change_type = fields.Selection([('add', 'Add'), 
		('remove', 'Remove'), ('update', 'Update')], string="Type")
	new_bom_id = fields.Many2one('mrp.bom', string="New Bill of Materials")
	new_bom_revision = fields.Many2one('mrp.bom.revision', string="Bom Revision Number")


	@api.multi
	def compute_qty(self):
		for line in self:
			delta = line.new_product_qty - line.old_product_qty
			line.upd_product_qty = delta



	