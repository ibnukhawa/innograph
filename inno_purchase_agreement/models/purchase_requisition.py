# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class PurchaseRequisition(models.Model):
	_inherit = "purchase.requisition"

	state = fields.Selection([('draft', 'Draft'), ('in_progress', 'To Approve'),
							  ('open', 'Approved'), ('done', 'Done'),
							  ('cancel', 'Cancelled')],
							 'Status', track_visibility='onchange', required=True,
							 copy=False, default='draft')
	approver_id = fields.Many2one('res.partner', string="Approver")

	def action_in_progress(self):
		if not self.approver_id:
			raise UserError(_("Approver still empty."))
		email = self.env.ref("inno_purchase_agreement.approver_notification_email")
		# Process to get data information for email contents #####
		list_products_description = self.line_ids.sorted('id').mapped('product_id').mapped('display_name')
		list_products_description = ', '.join(list_products_description)
		project = "-"
		project_ids = self.account_analytic_id.project_ids
		if len(project_ids) > 0:
			project = project_ids[0].code
		purchase_amount = sum([x.price_unit * x.product_qty for x in self.line_ids])
		context = {
			'list_product': list_products_description,
			'purchase_amount': purchase_amount,
			'project': project
		}
		email.with_context(data=context).send_mail(self.id, force_send=True)
		return super(PurchaseRequisition, self).action_in_progress()

	def action_open(self):
		active_user_id = self.env.user.partner_id.id
		if self.approver_id.id != active_user_id:
			raise UserError(_("You don’t have any access to approve this request."))
		
		list_products_description = self.line_ids.sorted('id').mapped('product_id').mapped('display_name')
		list_products_description = ', '.join(list_products_description)
		project = "-"
		project_ids = self.account_analytic_id.project_ids
		if len(project_ids) > 0:
			project = project_ids[0].code
		email = self.env.ref("inno_purchase_agreement.purchase_notification_email")
		user = self.user_id
		purchase_amount = sum([x.price_unit * x.product_qty for x in self.line_ids])
		context = {
			'name': user.name,
			'email': user.partner_id.email,
			'list_product': list_products_description,
			'purchase_amount': purchase_amount,
			'project': project
		}
		email.with_context(data=context).send_mail(self.id, force_send=True)
		return super(PurchaseRequisition, self).action_open()
