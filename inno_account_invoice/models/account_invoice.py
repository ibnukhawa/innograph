# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import UserError

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    date_payment = fields.Date(string="Payment Date", compute="_compute_date_payment")
    project_code_id = fields.Char(string="Project Code", store=True, compute="_compute_project_code_sme")
    sme_id = fields.Many2one('project.sme', string="SME", store=True, compute="_compute_project_code_sme")

    @api.multi
    def _compute_date_payment(self):
        for invoice in self:
            payment_ids = invoice.payment_ids
            payment_date = payment_ids.mapped('payment_date')
            if any(payment_date):
                invoice.date_payment = max(payment_date)

    @api.multi
    @api.depends('invoice_line_ids', 'invoice_line_ids.account_analytic_id')
    def _compute_project_code_sme(self):
        for invoice in self:
            projects = invoice.invoice_line_ids.mapped('account_analytic_id')
            if any(projects):
                invoice.project_code_id = projects[0].code
                invoice.sme_id = projects[0].sme_id


