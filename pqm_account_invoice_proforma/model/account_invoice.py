# -*- coding: utf-8 -*-
"""pqm_account_invoice_proforma"""
from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import UserError, RedirectWarning, ValidationError

class AccountJournal(models.Model):
    """class account_journal"""
    _inherit = "account.journal"

    is_accrued_journal = fields.Boolean(string="Accrued Journal")

class AccountInvoice(models.Model):
    """class account_invoice"""
    _inherit = "account.invoice"

    accrued_journal = fields.Many2one('account.move')
    accrued_reverse_journal = fields.Many2one('account.move')

    @api.multi
    def action_move_accrued(self):
        """ Creates invoice related analytics and financial move lines """
        account_move = self.env['account.move']
        journal_ids = self.env['account.journal']
        for inv in self:
            name = inv.name or '/'
            date_inv = datetime.now()
            journal = journal_ids.search([('is_accrued_journal','=', True)])
            if not journal:
                raise UserError(_("Journal with setting True Boolean 'Accrued Journal' is not yet."))
            date = inv.date_invoice or date_inv
            move_line = []
            part = inv.partner_id.id
            for line in self.invoice_line_ids:
                if line.quantity==0:
                    continue
                price = line.price_unit * line.quantity
                if not line.account_analytic_id.project_type_id.accrued_sale_id:
                    raise UserError(_("Accrued Sales on Project type is not set."))

                line_debit_vals = {'name': 'PROFORMA',
                             'analytic_account_id': line.account_analytic_id.id,
                             'debit': price,
                             'quantity': line.quantity,
                             'account_id': line.account_analytic_id.project_type_id.accrued_sale_id.id,
                             'partner_id': part,
                             }
                move_line.append(((0, 0, line_debit_vals)))
                line_credit_vals = {'name': line.name.split('\n')[0][:64],
                             'analytic_account_id': line.account_analytic_id.id,
                             'credit': price,
                             'quantity': line.quantity,
                             'account_id': line.account_analytic_id.project_type_id.income_account_id.id,
                             'partner_id': part,
                             }
                move_line.append(((0, 0, line_credit_vals)))
            move_vals = {
                'name': name,
                'ref': inv.proforma_nmbr,
                'line_ids': move_line,
                'journal_id': journal.id,
                'date': date,
                'narration': inv.comment,
                'company_id': inv.company_id.id
            }
            move = account_move.create(move_vals)
            print move
            move.post()
            vals = {
                'accrued_journal': move.id,
            }
            inv.write(vals)
        return True

    @api.multi
    def invoice_validate(self):
        res = super(AccountInvoice, self).invoice_validate()
        for invoice in self:
            if invoice.accrued_journal:
                move = self.env['account.move'].search([('id','=', invoice.accrued_journal.id)])
                reverse=move.reverse_moves(date=None, journal_id=None)
                for rev in reverse:
                    move_rev=self.env['account.move'].search([('id','=', rev)])
                    invoice.write({'accrued_reverse_journal': move_rev.id})
        return res

    @api.multi
    def action_cancel(self):
        res = super(AccountInvoice, self).action_cancel()
        moves = self.env['account.move']
        for inv in self:
            if inv.accrued_journal:
                moves += inv.accrued_journal
            if inv.accrued_reverse_journal:
                moves += inv.accrued_reverse_journal
        self.write({'accrued_journal': False, 'accrued_reverse_journal': False,})
        if moves:
            moves.button_cancel()
            moves.unlink()
        return res

