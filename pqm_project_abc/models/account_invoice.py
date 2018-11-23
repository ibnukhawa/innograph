# -*- coding: utf-8 -*-
""" pqm_project_abc """
from odoo import fields, api, models


class AccountInvoice(models.Model):
    """class account invoice"""
    _inherit = "account.invoice"

    @api.model
    def tax_line_move_line_get(self):
        """
            Extend function to set account_analytic_id False
        """
        res = super(AccountInvoice, self).tax_line_move_line_get()
        for tax in res:
            tax.update({'account_analytic_id': False})

        return res
