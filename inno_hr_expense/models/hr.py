# -*- coding: utf-8 -*-
""" Import """
from datetime import date
from odoo import fields, models, api, _
from odoo.exceptions import UserError
import odoo.addons.decimal_precision as dp


class Employee(models.Model):
    """ Inherit Employee """
    _inherit = 'hr.employee'

    medical_reimbursement = fields.Float(string="Medical (%)", default=0.00)
    medical_budget = fields.Float(string="Budget Medical",
                                  default=0.00, store=True, compute="_compute_medical_budget")
    medical_consum = fields.Float(string="Consumed Medical",
                                  default=0.00, compute="_compute_medical_consum")

    @api.multi
    def _compute_medical_consum(self):
        """ Compute function for Medical Consumed"""
        start = date(date.today().year, 1, 1)
        end = date(date.today().year, 12, 31)
        expense_obj = self.env['hr.expense']
        for emp in self:
            expense_ids = expense_obj.search([('employee_id', '=', emp.id),
                                              ('date', '>=', start),
                                              ('date', '<=', end),
                                              ('state', 'in', ['done'])])
            expense_ids = expense_ids.filtered(
                lambda x: x.category_id.is_medical or x.product_id.categ_id.is_medical)
            emp.medical_consum = sum(expense_ids.mapped('total_amount'))

    @api.multi
    @api.depends('medical_reimbursement', 'contract_ids', 'contract_ids.wage')
    def _compute_medical_budget(self):
        """ Compute function for Medical Budget """
        for emp in self:
            contract = False
            if emp.contract_id and emp.contract_id.state == 'open':
                contract = emp.contract_id
            elif any(emp.contract_ids.filtered(lambda x: x.state == 'open')):
                running_contract = emp.contract_ids.filtered(lambda x: x.state == 'open')
                running_contract = running_contract.sorted('date_start desc', reverse=True)
                contract = running_contract[0]

            if contract:
                emp.medical_budget = contract.wage * (emp.medical_reimbursement / 100)

    def _check_medical_reimbursement(self):
        """ Function to constraint medical reimbursement to have value between 0 and 100 """
        for emp in self:
            if emp.medical_reimbursement > 100 or emp.medical_reimbursement < 0:
                return False
            else:
                return True

    _constraints = [
        (_check_medical_reimbursement, 'Invalid Value for Medical Reimbursement',
         ['medical_reimbursement'])
    ]


class HrExpense(models.Model):
    """ Inherit Expense """
    _inherit = 'hr.expense'

    requested_amount = fields.Float(string='Requested Total', store=True, compute='_compute_amount',
                                    digits=dp.get_precision('Account'))

    @api.depends('quantity', 'unit_amount', 'tax_ids', 'currency_id')
    def _compute_amount(self):
        """
            Replace to compute new field requested amount
            And Add medical reimbursement percentage
        """
        for expense in self:
            medical_reimbursement = expense.employee_id.medical_reimbursement
            category_id = expense.category_id or expense.product_id.categ_id
            taxes = expense.tax_ids.compute_all(expense.unit_amount, expense.currency_id,
                                                expense.quantity, expense.product_id,
                                                expense.employee_id.user_id.partner_id)
            if not category_id.is_medical:
                expense.untaxed_amount = expense.unit_amount * expense.quantity
                expense.total_amount = taxes.get('total_included')
            else:
                expense.untaxed_amount = (medical_reimbursement / 100) * (
                    expense.unit_amount * expense.quantity)
                expense.total_amount = (medical_reimbursement / 100) * taxes.get('total_included')
            expense.requested_amount = taxes.get('total_included')

    @api.multi
    def _move_line_get(self):
        """ Replace to adjust total with medical reimbursement when product category is medical """
        account_move = []
        for expense in self:
            move_line = expense._prepare_move_line_value()
            account_move.append(move_line)

            # Calculate tax lines and adjust base line
            taxes = expense.tax_ids.with_context(round=True).compute_all(expense.unit_amount,
                                                                         expense.currency_id,
                                                                         expense.quantity,
                                                                         expense.product_id)
            # Change amount total if Medical reimbursement
            category_id = expense.category_id or expense.product_id.categ_id
            if category_id.is_medical:
                medical_reimbursement = expense.employee_id.medical_reimbursement
                taxes['total_excluded'] = taxes['total_excluded'] * (medical_reimbursement / 100)

            account_move[-1]['price'] = taxes['total_excluded']
            account_move[-1]['tax_ids'] = [(6, 0, expense.tax_ids.ids)]
            for tax in taxes['taxes']:
                account_move.append({
                    'type': 'tax',
                    'name': tax['name'],
                    'price_unit': tax['amount'],
                    'quantity': 1,
                    'price': tax['amount'],
                    'account_id': tax['account_id'] or move_line['account_id'],
                    'tax_line_id': tax['id'],
                })
        return account_move

    @api.onchange('price_amount', 'total_amount', 'quantity')
    def onchange_total_amount(self):
        """
            Add onchange function in Expense, will check if User adjustment still
            have Expense consumed larger than it's budget
        """
        if self.sheet_id:
            sheet = self.sheet_id
            medical_expense = sheet.expense_line_ids.filtered(
                lambda x: x.category_id.is_medical or x.product_id.categ_id.is_medical)
            new_expense_consumed = sum(medical_expense.mapped('total_amount'))
            budget = self.employee_id.medical_budget
            if new_expense_consumed > budget:
                raise UserError(_("Your Medical Budget already reach the yearly limit \
                                  (Your Budget = %s, Consumed Budget = %s).\n \
                                   You can continue to ask approval, \
                                   or adjust the expense amount." % (budget, new_expense_consumed)))


class HrExpenseSheet(models.Model):
    """ Inherit Expense Sheet """
    _inherit = 'hr.expense.sheet'

    requested_amount = fields.Float(string='Total Requested Amount', store=True,
                                    compute='_compute_requested_amount',
                                    digits=dp.get_precision('Account'))

    @api.multi
    @api.depends('expense_line_ids', 'expense_line_ids.requested_amount',
                 'expense_line_ids.currency_id')
    def _compute_requested_amount(self):
        """ Compute function for requested amount """
        for sheet in self:
            total_amount = 0.0
            for expense in sheet.expense_line_ids:
                total_amount += expense.currency_id.with_context(
                    date=expense.date,
                    company_id=expense.company_id.id
                ).compute(expense.requested_amount, sheet.currency_id)
            sheet.requested_amount = total_amount

    @api.onchange('expense_line_ids')
    def _onchange_expense_line_ids(self):
        """
            Add onchange function to Check expense consume larger than expense budget
            when user add line on Expense line
        """
        medical_expense = self.expense_line_ids.filtered(
            lambda x: x.category_id.is_medical or x.product_id.categ_id.is_medical)
        expense_total = sum(medical_expense.mapped('total_amount'))
        new_expense_consumed = expense_total + self.employee_id.medical_consum
        budget = self.employee_id.medical_budget
        if new_expense_consumed > budget:
            raise UserError(_("Your Medical Budget already reach the yearly limit \
                              (Your Budget = %s, Consumed Budget = %s).\n \
                               You can continue to ask approval, \
                               or adjust the expense amount." % (budget, new_expense_consumed)))
