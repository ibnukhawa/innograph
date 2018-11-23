# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import time

from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    invoice_date = fields.Date('Invoice Date')

    @api.multi
    def _create_invoice(self, order, so_line, amount):
        res = super(SaleAdvancePaymentInv, self)._create_invoice(order, so_line, amount)
        if self.invoice_date:
            res.write({'date_invoice': self.invoice_date})

    @api.multi
    def create_invoices(self):
        sale_orders = self.env['sale.order'].browse(self._context.get('active_ids', []))
        invoice = self.env['account.invoice']
        if self.invoice_date:
            if self.advance_payment_method == 'delivered':
                inv_id = sale_orders.action_invoice_create()
                inv = invoice.search([('id', 'in', inv_id)])
                inv.write({'date_invoice': self.invoice_date})
            elif self.advance_payment_method == 'all':
                inv_id = sale_orders.action_invoice_create(final=True)
                inv = invoice.search([('id', 'in', inv_id)])
                inv.write({'date_invoice': self.invoice_date})
            else:
                super(SaleAdvancePaymentInv, self).create_invoices()
                
            if self._context.get('open_invoices', False):
                return sale_orders.action_view_invoice()
            return {'type': 'ir.actions.act_window_close'}
        else:
            super(SaleAdvancePaymentInv, self).create_invoices()

