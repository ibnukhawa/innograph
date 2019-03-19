# -*- coding: utf-8 -*-
""" pqm_hr_expense_approval """
from odoo import fields, api, models, _

class ResUsers(models.Model):
    """ pqm_hr_expense_approval """
    _inherit = "res.users"

    is_approval = fields.Boolean(string = "Is Approval Expenses")
    is_validator = fields.Boolean(string = "Is Validator Expenses")

    @api.multi
    def write(self, values):
        res = super(ResUsers, self).write(values)
        if values.get('is_approval') :
            group = self.env.ref('hr_expense.group_hr_expense_user')
            group_id = group.id
            self.write({
                        'groups_id': [(4, group_id)]
                        })
        if values.get('is_validator') :
            group = self.env.ref('pci_hr_expense_validate.hr_expense_validate_user')
            group_id = group.id
            self.write({
                        'groups_id': [(4, group_id)]
                        })
        return res
