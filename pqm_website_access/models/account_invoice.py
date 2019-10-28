# -*- coding: utf-8 -*-
from odoo import api, fields, models


class AccountInvoice(models.Model):
	_inherit = "account.invoice"

	origin_url = fields.Char('URL Origin')


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    @api.multi
    def _create_invoice(self, order, so_line, amount):
    	invoice = super(SaleAdvancePaymentInv, self)._create_invoice(order, so_line, amount)
		if invoice:
			invoice.write({'origin_url': order.origin_url})
    	return invoice
