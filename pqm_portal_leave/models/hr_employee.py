# pylint: disable=import-error,protected-access,too-few-public-methods
"""Inherit HR Holidays"""
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class HrEmployee(models.Model):
    """Custom employee menu"""
    _inherit = "hr.employee"

    coach = fields.Boolean('Is a Coach')

    @api.multi
    def write(self, vals):
        group_holiday_manager = self.env.ref('hr_holidays.group_hr_holidays_manager')
        if vals.get('coach_id') != False:
            coach = self.search([('id','=',vals.get('coach_id'))],limit=1)
            if coach:
                if coach.user_id:
                    group_holiday_manager.sudo().write({'users': [(4, coach.user_id.id)]})
                else:
                    raise UserError(_("%s has no user account!" % (coach.name)))
        if vals.get('coach_id') == False:
            subordinate = self.search([('id', '!=', self.id),('coach_id', '=', self.coach_id.id)])
            if not subordinate:
                if self.coach_id.user_id:
                    group_holiday_manager.sudo().write({'users': [(3, self.coach_id.user_id.id)]})
        return super(HrEmployee, self).write(vals)

    @api.model
    def recompute_coach_leave(self):
        group_holiday_manager = self.env.ref('hr_holidays.group_hr_holidays_manager')
        emp_coach_list = self.search([("coach_id", "!=", False)]).mapped("coach_id")
        list_user = []
        for coach in emp_coach_list:
            if coach.user_id:
                list_user.append((4, coach.user_id.id))
        if list_user:
            group_holiday_manager.sudo().write({'users': list_user})
