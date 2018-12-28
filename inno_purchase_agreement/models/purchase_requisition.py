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
		symbol = self.company_id.currency_id.symbol
		purchase_amount = ("%s %s" % (symbol, "{:,.2f}".format(purchase_amount)))
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
		purchase_amount = sum([x.price_unit * x.product_qty for x in self.line_ids])
		symbol = self.company_id.currency_id.symbol
		purchase_amount = ("%s %s" % (symbol, "{:,.2f}".format(purchase_amount)))
		context = {
			'list_product': list_products_description,
			'purchase_amount': purchase_amount,
			'project': project
		}
		email.with_context(data=context).send_mail(self.id, force_send=True)
		return super(PurchaseRequisition, self).action_open()

class PurchaseRequisitionLine(models.Model):
	_inherit = 'purchase.requisition.line'

	sale_order_id = fields.Many2one('sale.order', string="Sales Order")

class PurchaseOrder(models.Model):
	""" Inherit Purchase Order """
	_inherit = 'purchase.order'

	@api.onchange('requisition_id')
	def _onchange_requisition_id(self):
		""" 
			Replace function to add sale order id 
			when create purchase order line when create new quotation 
		"""
		if not self.requisition_id:
			return

		requisition = self.requisition_id
		if self.partner_id:
			partner = self.partner_id
		else:
			partner = requisition.vendor_id
		payment_term = partner.property_supplier_payment_term_id
		currency = partner.property_purchase_currency_id or requisition.company_id.currency_id

		FiscalPosition = self.env['account.fiscal.position']
		fpos = FiscalPosition.get_fiscal_position(partner.id)
		fpos = FiscalPosition.browse(fpos)

		self.partner_id = partner.id
		self.fiscal_position_id = fpos.id
		self.payment_term_id = payment_term.id,
		self.company_id = requisition.company_id.id
		self.currency_id = currency.id
		self.origin = requisition.name
		self.partner_ref = requisition.name # to control vendor bill based on agreement reference
		self.notes = requisition.description
		self.date_order = requisition.date_end or fields.Datetime.now()
		self.picking_type_id = requisition.picking_type_id.id

		if requisition.type_id.line_copy != 'copy':
			return

		order_lines = []
		for line in requisition.line_ids:
			product_lang = line.product_id.with_context({
				'lang': partner.lang,
				'partner_id': partner.id,
			})
			name = product_lang.display_name
			if product_lang.description_purchase:
				name += '\n' + product_lang.description_purchase

			if fpos:
				taxes_ids = fpos.map_tax(line.product_id.supplier_taxes_id.filtered(lambda tax: tax.company_id == requisition.company_id)).ids
			else:
				taxes_ids = line.product_id.supplier_taxes_id.filtered(lambda tax: tax.company_id == requisition.company_id).ids

			if line.product_uom_id != line.product_id.uom_po_id:
				product_qty = line.product_uom_id._compute_quantity(line.product_qty, line.product_id.uom_po_id)
				price_unit = line.product_uom_id._compute_price(line.price_unit, line.product_id.uom_po_id)
			else:
				product_qty = line.product_qty
				price_unit = line.price_unit

			if requisition.type_id.quantity_copy != 'copy':
				product_qty = 0

			if requisition.company_id.currency_id != currency:
				price_unit = requisition.company_id.currency_id.compute(price_unit, currency)

			sale_id = False
			if line.sale_order_id:
				sale_id = line.sale_order_id.id

			order_lines.append((0, 0, {
				'name': name,
				'product_id': line.product_id.id,
				'product_uom': line.product_id.uom_po_id.id,
				'sale_order_id': sale_id,
				'product_qty': product_qty,
				'price_unit': price_unit,
				'taxes_id': [(6, 0, taxes_ids)],
				'date_planned': requisition.schedule_date or fields.Date.today(),
				'procurement_ids': [(6, 0, [requisition.procurement_id.id])] if requisition.procurement_id else False,
				'account_analytic_id': line.account_analytic_id.id,
			}))
		self.order_line = order_lines