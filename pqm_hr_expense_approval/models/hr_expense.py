# -*- coding: utf-8 -*-
"""pqm_hr_expense_approval"""
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class HrExpenseSheet(models.Model):
    """class hr_expense_sheet"""
    _inherit = "hr.expense.sheet"

    category_id = fields.Many2one('product.category', string="Product Category")
    approval_id = fields.Many2one('res.users', string="Approval", domain=[('is_approval', '=', True)])
    validate_id = fields.Many2one(
        'res.users', string='Validate', track_visibility='onchange', domain=[('is_validator', '=', True)])

    @api.onchange('category_id')
    def onchange_category(self):
        domain = {}
        if self.category_id:
            self.validate_id = self.category_id.validate_id
            categ = {'expense_line_ids': [('category_id', '=', self.category_id.id),('state','=','draft')]}
            return {'domain': categ}

    @api.model
    def create(self, vals):
        res = super(HrExpenseSheet, self).create(vals)
        print res, '================'
        res.expense_send_email()
        return res


    @api.multi
    def validate_expense_sheets(self):
        for sheet in self:
            if sheet.validate_id:
                if sheet.env.user != sheet.validate_id:
                    raise UserError(_('Sorry, You can not have access validate. Because only %s can validate this Expense' % sheet.validate_id.name))
                sheet.write({'state': 'validate'})
                sheet.expense_approve_send_email(self.id)
            else:
                sheet.expense_approve_send_email(self.id)
                return super(HrExpenseSheet, sheet).validate_expense_sheets()

    @api.multi
    def approve_expense_sheets(self):
        for sheet in self:
            res = super(HrExpenseSheet, sheet).approve_expense_sheets()
            if sheet.approval_id:
                if sheet.env.user != sheet.approval_id:
                    raise UserError(_('Sorry, You can not have access Approval. Because only %s can Approve this Expense' % sheet.approval_id.name))
            return res

    @api.multi
    def expense_send_email(self):
        """
        send email to user validate if the state is submit
        """
        template_id = self.env.\
            ref('pqm_hr_expense_approval.expense_submit_email_template')
        print template_id,'================'
        for rec in self:
            template_id.write({
                'email_to': rec.validate_id.email,
            })
            template_id.\
                with_context(validate=rec.validate_id.name,
                             expense_name=rec.name).\
                send_mail(rec.id, force_send=True)

    @api.model
    def expense_approve_send_email(self, rec_id):
        """
        send email to user Approval if the state is validate
        """
        template_id = self.env.\
            ref('pqm_hr_expense_approval.expense_validate_email_template')
        print template_id,'================'
        for rec in self:
            template_id.write({
                'email_to': rec.approval_id.email,
            })
            template_id.\
                with_context(approver=rec.approval_id.name,
                             validator=rec.validate_id.name,
                             expense_name=rec.name).\
                send_mail(rec_id, force_send=True)
                


class HrExpense(models.Model):
    """class hr_expense"""
    _inherit = "hr.expense"

    category_id = fields.Many2one('product.category', string="Product Category")

    @api.model
    def create(self, vals):
        res = super(HrExpense, self).create(vals)
        if vals.get('account_id'):
            account = self.env['account.account'].search([('id','=', vals.get('account_id'))])
            if account.deprecated:
                raise UserError(_('Sorry, This Account " %s " is already deprecated' % account.name))
        return res

    @api.multi
    def write(self, vals):
        res = super(HrExpense, self).write(vals)
        for exp in self:
            if vals.get('sheet_id'):
                if exp.category_id == False:
                    exp.category_id = exp.sheet_id.category_id
            if vals.get('account_id'):
                if exp.account_id.deprecated:
                    raise UserError(_('Sorry, This Account " %s " is already deprecated' % exp.account_id.name))
        return res
    
    @api.onchange('category_id')
    def onchange_category(self):
        domain = {}
        if self.category_id:
            categ = {'product_id': [('categ_id', '=', self.category_id.id)]}
            return {'domain': categ}
    
