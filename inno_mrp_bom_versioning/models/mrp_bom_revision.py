# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class MrpBomRevision(models.Model):
	_name = "mrp.bom.revision"

	name = fields.Char()
	product_tmpl_id = fields.Many2one('product.template', track_visibility='always', 
		string="Product Template", domain=[('bom_ids', '!=', False)])
	bom_id = fields.Many2one('mrp.bom', track_visibility='always', string="Bill of Materials")
	responsible_id = fields.Many2one('res.users', track_visibility='always', string="Responsible", default=lambda self: self.env.user)
	approver_id = fields.Many2one('res.users', track_visibility='always', string="Approver")
	state = fields.Selection([('draft', 'Draft'),
							  ('submit', 'Submitted'),
							  ('approve', 'Approved'),
							  ('reject', 'Rejected'),
							  ('cancel', 'Cancelled')
							 ], track_visibility='always', string="Status", default="draft")
	note = fields.Text()
	bom_change_ids = fields.One2many('mrp.bom.revision.change', 'bom_revision_id', 
		string="Bom Change Lines")
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
		view = self.env.ref("inno_bom_revision.mrp_bom_revision_change_tree_view")
		change_ids = []
		if not self.bom_change_ids:
			bom_id = self.bom_id
			change_obj = self.env['mrp.bom.revision.change']
			for line in bom_id.bom_line_ids:
				new_line = change_obj.create({'product_id': line.product_id.id,
											  'old_product_qty': line.product_qty,
											  'new_product_qty': line.product_qty,
											  'old_uom_id': line.product_uom_id.id,
											  'new_uom_id': line.product_uom_id.id,
											  'change_type': 'update',
											  'bom_revision_id': self.id
											})
		return {
			'name': _("BOM Revision Change"),
			'type': 'ir.actions.act_window',
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'mrp.bom.revision.change',
			'views': [(view.id, 'tree')],
			'view_id': view.id,
			'target': 'current',
			'domain': [('bom_revision_id', '=', self.id)],
			'context': {'default_bom_revision_id': self.id},
		}

	def _check_responsible(self):
		if self.responsible_id.id == self.env.user.id:
			self.is_responsible = True

	def _check_approver(self):
		if self.approver_id.id == self.env.user.id:
			self.is_approver = True

	def compute_revision_count(self):
		product = self.product_tmpl_id
		rev_src = self.env['mrp.bom.revision'].search([
			('product_tmpl_id', '=', product.id), ('state', 'not in', ['cancel', 'reject'])])
		self.revision_count = len(rev_src)

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
		new_bom = self.bom_id.copy()
		new_bom.bom_line_ids = False
		for line in self.bom_change_ids.filtered(lambda x: x.change_type != 'remove'):
			vals = {
				'product_id': line.product_id.id,
				'product_qty': line.new_product_qty,
				'product_uom_id': line.new_uom_id.id,
				'bom_id': new_bom.id,
			}
			new_bom_line = self.env['mrp.bom.line'].create(vals)
			new_bom.write({'bom_line_ids': [(4, new_bom_line.id)]})
			line.write({'new_bom_id': new_bom.id})
		self.bom_id.active = False

class MrpBomRevisionChange(models.Model):
	_name = "mrp.bom.revision.change"

	new_product_qty = fields.Float(string="New Revision Qty")
	old_product_qty = fields.Float(string="Previous Revision Qty")
	upd_product_qty = fields.Float(string="Quantity", compute="compute_qty")
	bom_revision_id = fields.Many2one('mrp.bom.revision', string="Bom Revision")
	old_uom_id = fields.Many2one('product.uom', related="product_id.uom_id", string="Previous Product Uom")
	new_uom_id = fields.Many2one('product.uom', related="product_id.uom_id", string="New Product Uom")
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



	