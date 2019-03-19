from odoo import fields, api, models, _
from odoo.exceptions import UserError

class HrEmployee(models.Model):
    _inherit = "hr.employee"

    @api.multi
    def write(self, vals):
        group_attendance_officer = self.env.ref('hr_attendance.group_hr_attendance_user')
        if vals.get('coach_id') != False:
            coach = self.browse(vals.get('coach_id'))
            if coach:
                if coach.user_id:
                    group_attendance_officer.sudo().write({'users': [(4, coach.user_id.id)]})
                else:
                    raise UserError(_("%s has no user account!" % (coach.name)))
        if vals.get('coach_id') == False:
            subordinate = self.search([('id', '!=', self.id), ('coach_id', '=', self.coach_id.id)])
            if not subordinate:
                if self.coach_id.user_id:
                    group_attendance_officer.sudo().write({'users': [(3, self.coach_id.user_id.id)]})
        return super(HrEmployee, self).write(vals)

    @api.model
    def recompute_coach_attendance(self):
        group_attendance_officer = self.env.ref('hr_attendance.group_hr_attendance_user')
        emp_coach_list = self.search([("coach_id", "!=", False)]).mapped("coach_id")
        list_user = []
        for coach in emp_coach_list:
            if coach.user_id:
                list_user.append((4, coach.user_id.id))
        if list_user:
            group_attendance_officer.sudo().write({'users': list_user})
