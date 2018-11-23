""" pqm_project_abc"""
from datetime import datetime
from odoo import fields, models, api, _
from odoo.exceptions import UserError


class AccountMove(models.Model):
    """ pqm_project_abc"""
    _inherit = "account.move"

    timesheet_id = fields.Many2one('hr_timesheet_sheet.sheet', string='Timesheet')

class HrTimesheetSheet(models.Model):
    """ pqm_project_abc"""
    _inherit = "hr_timesheet_sheet.sheet"

    @api.multi
    def action_timesheet_done(self):
        res = super(HrTimesheetSheet, self).action_timesheet_done()
        for i in self:
            journal_id = self.env['ir.values'].get_default('project.config.settings', 'timesheet_journal_id')
            partner = i.employee_id.user_id.partner_id
            for line in i.timesheet_ids:
                if line.project_id.project_type_id.income_account_id:
                    if i.employee_id.timesheet_cost == 0 or i.employee_id.overhead_cost == 0:
                        raise UserError(_("Timesheet Cost and Overhead Cost in Employee "
                                          "Form must be Filled  and not less than or equal to 0"))
                    else:
                        date_from = datetime.strptime(i.date_from, '%Y-%m-%d')
                        date_from2 = date_from.strftime('%m-%d-%Y')
                        date_to = datetime.strptime(i.date_from, '%Y-%m-%d')
                        date_to2 = date_to.strftime('%m-%d-%Y')
                        period = 'Timesheet Periods '+date_from2+' to '+date_to2
                        
                        date = line.date
                        partner_id = partner.id
                        name = line.name
                        name_line = partner.name + ' ' + line.name
                        account_id = line.project_id.analytic_account_id.id
                        qty = line.unit_amount
                        ref = line.name +' ' + partner.name + ' '+ period
                        analytic_account_id = line.project_id.analytic_account_id.id
                        
                        value_salary = line.unit_amount * i.employee_id.timesheet_cost
                        acc_salary = line.project_id.project_type_id.salary_account_id.id
                        
                        value_overhead = line.unit_amount * i.employee_id.overhead_cost
                        acc_overhead = line.project_id.project_type_id.overhead_account_id.id
                        
                        value_salary_allocation = value_salary + value_overhead
                        acc_salary_allocation = line.project_id.project_type_id.accrued_expense_id.id
                        
                        salary_allocation = {
                            'date_maturity': date,
                            'partner_id': partner_id,
                            'name': name,
                            'debit': 0,
                            'credit': value_salary_allocation,
                            'account_id': acc_salary_allocation,
                            'amount_currency': 0,
                            'currency_id': False,
                            'quantity': qty,
                            'product_id': False,
                            'product_uom_id': False,
                        }
                        salary = {
                            'date_maturity': date,
                            'partner_id': partner_id,
                            'name': name,
                            'debit': value_salary,
                            'credit': 0,
                            'account_id': acc_salary,
                            'analytic_line_ids': [(0, 0, {
                                'name': name_line,
                                'partner_id': partner_id,
                                'date': date,
                                'account_id': account_id,
                                'unit_amount': qty,
                                'amount': value_salary,
                                'product_id': False,
                                'product_uom_id': False,
                                'general_account_id': acc_salary,
                                'ref': ref,
                                })],
                            'amount_currency': 0,
                            'currency_id': False,
                            'quantity': qty,
                            'product_id': False,
                            'product_uom_id': False,
                            'analytic_account_id': analytic_account_id,
                        }
                        overhead = {
                            'date_maturity': date,
                            'partner_id': partner_id,
                            'name': name,
                            'debit': value_overhead,
                            'credit': 0,
                            'account_id': acc_overhead,
                            'analytic_line_ids': [(0, 0, {
                                'name': name_line, 
                                'partner_id': partner_id,
                                'date': date,
                                'account_id': account_id,
                                'unit_amount': qty,
                                'amount': value_overhead,
                                'product_id': False,
                                'product_uom_id': False,
                                'general_account_id': acc_overhead,
                                'ref': ref,
                                })],
                            'amount_currency': 0,
                            'currency_id': False,
                            'quantity': qty,
                            'product_id': False,
                            'product_uom_id': False,
                            'analytic_account_id': analytic_account_id,
                        }
                        am = {
                            'date': line.date,
                            'journal_id': journal_id,
                            'ref': period,
                            'timesheet_id': self.id,
                            'line_ids': [(0, 0, overhead), (0, 0, salary_allocation), (0, 0, salary)]
                            }
                        create_am = self.env['account.move'].sudo().create(am)
                        create_am.post()
        return res

    @api.multi
    def action_timesheet_draft(self):
        res = super(HrTimesheetSheet, self).action_timesheet_draft()
        move_ids = self.env['account.move'].sudo().search([('timesheet_id','=',self.id)])
        if move_ids:
            move_ids.button_cancel()
            move_ids.unlink()
        return res

class AccountAnalyticLine(models.Model):
    """ pqm_project_abc"""
    _inherit = "account.analytic.line"

    @api.multi
    def write(self, vals):
        """ 
            Extend function write to add condition for timesheet max 24 hours
        """

        if self.sheet_id and vals.get('unit_amount'):
            timesheet = self.env['account.analytic.line'].search(
                [('id','!=', self.id),('date', '=', self.date), ('sheet_id', '=', self.sheet_id.id)])
            hours = vals.get('unit_amount')
            if timesheet:
                for time in timesheet:
                    hours += time.unit_amount
            if hours > 24:
                raise UserError(_('The Total Timesheet Hours on %s more than 24 hour' % self.date))
        return super(AccountAnalyticLine, self).write(vals)
