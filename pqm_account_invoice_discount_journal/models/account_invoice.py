# pylint: disable=C0111,C0303,I0011,R0903
# -*- coding: utf-8 -*-
"""iherit account invoice"""
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class AccountInvoiceLine(models.Model):
    """account.invoice.line class"""
    _inherit = "account.invoice.line"
   
    discount_unit = fields.Monetary(string='Discount Unit', \
        store=True, readonly=True, compute='_compute_price')
    discount_total = fields.Monetary(string='Total Discount', \
        store=True, readonly=True, compute='_compute_price')
    price_before_discount = fields.Monetary(string='Price Before Discount', \
        store=True, readonly=True, compute='_compute_price')
    discount_account_id = fields.Many2one('account.account')

    @api.one
    @api.depends('price_unit', 'discount', 'invoice_line_tax_ids', 'quantity', \
        'product_id', 'invoice_id.partner_id', 'invoice_id.currency_id', 'invoice_id.company_id', \
        'invoice_id.date_invoice')
    def _compute_price(self):
        if not self.discount:
            res = super(AccountInvoiceLine, self)._compute_price()
            self.price_before_discount = self.price_subtotal
            self.discount_total = 0
            return res
        else:
            currency = self.invoice_id and self.invoice_id.currency_id or None
            discount = self.price_unit * (self.discount or 0.0) / 100.0
            price = self.price_unit - discount
            taxes = False
            taxes_discount = False
            if self.invoice_line_tax_ids:
                taxes = self.invoice_line_tax_ids.compute_all(price, currency, self.quantity, \
                                    product=self.product_id, partner=self.invoice_id.partner_id)
                taxes_discount = self.invoice_line_tax_ids.compute_all\
                    (discount, currency, self.quantity, \
                     product=self.product_id, partner=self.invoice_id.partner_id)
                
            self.price_subtotal = price_subtotal_signed = taxes['total_excluded'] if taxes else \
                                                            self.quantity * price
            self.discount_total = taxes_discount['total_excluded'] \
                if taxes else self.quantity * discount
            self.price_before_discount = self.price_subtotal + self.discount_total
            
            if self.invoice_id.currency_id and self.invoice_id.company_id and \
            self.invoice_id.currency_id != self.invoice_id.company_id.currency_id:
                price_subtotal_signed = self.invoice_id.currency_id.with_context \
                (date=self.invoice_id.date_invoice).compute(price_subtotal_signed, \
                                                            self.invoice_id.company_id.currency_id)
            sign = self.invoice_id.type in ['in_refund', 'out_refund'] and -1 or 1
            self.price_subtotal_signed = price_subtotal_signed * sign


class AccountInvoice(models.Model):
    """account.invoice class"""
    _inherit = "account.invoice"

    @api.model
    def invoice_line_move_line_get(self):
        any_discount = any([l.discount for l in self.invoice_line_ids])
        
        if not any_discount:
            res = super(AccountInvoice, self).invoice_line_move_line_get()
        else:
            res = []
            for line in self.invoice_line_ids:
                if line.quantity == 0:
                    continue
                discount_account_id = line.discount_account_id.id or self.journal_id.discount_account_id.id
                if line.discount>0 and not discount_account_id:
                    raise UserError(_('Please set discount account on Project Type of Project or on Journal %s.' % self.journal_id.name))

                tax_ids = []
                for tax in line.invoice_line_tax_ids:
                    tax_ids.append((4, tax.id, None))
                    for child in tax.children_tax_ids:
                        if child.type_tax_use != 'none':
                            tax_ids.append((4, child.id, None))
                analytic_tag_ids = [(4, analytic_tag.id, None) for analytic_tag in line.analytic_tag_ids]
    
                move_line_dict = {
                    'invl_id': line.id,
                    'type': 'src',
                    'name': line.name.split('\n')[0][:64],
                    'price_unit': line.price_unit,
                    'quantity': line.quantity,
                    'price': line.price_before_discount,
                    'account_id': line.account_id.id,
                    'product_id': line.product_id.id,
                    'uom_id': line.uom_id.id,
                    'account_analytic_id': line.account_analytic_id.id,
                    'tax_ids': tax_ids,
                    'invoice_id': self.id,
                    'analytic_tag_ids': analytic_tag_ids
                }
                if line['account_analytic_id']:
                    move_line_dict['analytic_line_ids'] = [(0, 0, line._get_analytic_line())]
                res.append(move_line_dict)
                
                #add discount
                move_line_dict = {
                    'invl_id': line.id,
                    'type': 'src',
                    'name': "Discount %s %% Product %s" % \
                            (line.discount, line.name.split('\n')[0][:64]),
                    'price_unit': line.discount_unit,
                    'quantity': line.quantity,
                    'price': line.discount_total*-1,
                    'account_id': discount_account_id,
                    'product_id': line.product_id.id,
                    'uom_id': line.uom_id.id,
                    'account_analytic_id': line.account_analytic_id.id,
                    'tax_ids': tax_ids,
                    'invoice_id': self.id,
                    'analytic_tag_ids': analytic_tag_ids
                }
                if line['account_analytic_id']:
                    move_line_dict['analytic_line_ids'] = [(0, 0, line._get_analytic_line())]
                res.append(move_line_dict)
        return res
