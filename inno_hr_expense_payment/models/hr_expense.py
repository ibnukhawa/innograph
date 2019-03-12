# -*- coding: utf-8 -*-
from odoo import api, fields, models


class HrExpenseSheet(models.Model):
    _inherit = 'hr.expense.sheet'

    payment_ids = fields.One2many('account.payment', compute='_compute_payment_ids')

    @api.multi
    def _compute_payment_ids(self):
        """
        This function is a roundabout way to find related payment, since there are no direct or
        indirect relation between expense report and payment.

        First, it search for all "extra" move lines from the reconciled journal entries related
        to the expense report. Afterwards, it filter all payments inside those move lines and
        show the filtered data inside the expense report.

        Of course, this method doesn't always works 100%. Sometimes, it unable to find any
        payments from all of the move lines in related journal entries. In other case, it
        might also show several other unrelated payments.
        """
        for sheet in self:
            if sheet.state != 'done':
                continue

            partner = sheet.mapped('employee_id.address_home_id')
            moves = self.env['account.move'].search([('ref', 'in', sheet.mapped('name'))])
            aml_ids = []

            for aml in moves.mapped('line_ids'):
                if aml.account_id.reconcile:
                    aml_ids.extend(
                        [r.debit_move_id.id for r in aml.matched_debit_ids] if aml.credit > 0 else [
                            r.credit_move_id.id for r in aml.matched_credit_ids])

            aml = self.env['account.move.line'].search([('id', 'in', aml_ids)])

            sheet.payment_ids = aml.mapped('payment_id').filtered(
                lambda l, emp=partner: l.partner_id in emp)

        return
