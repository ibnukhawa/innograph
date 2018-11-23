# -*- coding: utf-8 -*-
""" pqm_project_abc """
from odoo import api, models, _
from odoo import exceptions

class SaleOrderLine(models.Model):
    """ Class Sale Order Line """
    _inherit = "sale.order.line"

    @api.multi
    def _prepare_invoice_line(self, qty):
        """prepare to generate invoice line"""
        res = super(SaleOrderLine, self)._prepare_invoice_line(qty)
        if self.employee_id:
            res.update({'employee_id': self.employee_id.id})
            if self.order_id.project_id.project_type_id:
                income = self.order_id.project_id.project_type_id.income_account_id.id
                salary = self.order_id.project_id.project_type_id.salary_account_id.id
                expense = self.order_id.project_id.project_type_id.accrued_expense_id.id
                if not income or not salary or not expense:
                    raise exceptions.UserError(_(
                        'please complete account configuration on related project type.'))
                res.update({'account_id': income,
                            'salary_account_id': salary,
                            'accrued_expense_id': expense
                           })
        return res
