# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import UserError
import json

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    date_payment = fields.Date(string="Payment Date", store=True, compute="_compute_date_payment")
    project_code_id = fields.Char(string="Project Code", store=True, compute="_compute_project_code_sme")
    sme_id = fields.Many2one('project.sme', string="SME", store=True, compute="_compute_project_code_sme")

    @api.multi
    @api.depends('payment_ids', 'payments_widget','state')
    def _compute_date_payment(self):
        for invoice in self:
            if invoice.state=='paid':
                payment_ids = invoice.payment_ids
                payment_date = payment_ids.mapped('payment_date')
                # Get payment data from Payments
                if any(payment_date):
                    invoice.date_payment = max(payment_date)
                # Get payment data from payment widget (Paid with Bank Statement)
                elif invoice.payments_widget:
                    payment = json.loads(invoice.payments_widget)
                    if payment and any(payment.get('content', False)):
                        content = payment.get('content')
                        invoice.date_payment = content[0].get('date', False)
            else:
                invoice.date_payment=False

    @api.multi
    @api.depends('invoice_line_ids', 'invoice_line_ids.account_analytic_id')
    def _compute_project_code_sme(self):
        for invoice in self:
            projects = invoice.invoice_line_ids.mapped('account_analytic_id')
            if any(projects):
                invoice.project_code_id = projects[0].code
                invoice.sme_id = projects[0].sme_id


