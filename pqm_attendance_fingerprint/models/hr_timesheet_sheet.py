from datetime import datetime, timedelta
from odoo import fields, api, models, _
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT,DEFAULT_SERVER_DATE_FORMAT
import pytz


class HrTimesheetSheet(models.Model):
    _inherit = "hr_timesheet_sheet.sheet"

    @api.multi
    def check_employee_attendance_state(self):
        """ Checks the attendance records of the timesheet, make sure they are all closed
            (by making sure they have a check_out time)
        """
        self.ensure_one()
        return True


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    @api.model
    def create(self, vals):
        res = super(AccountAnalyticLine, self).create(vals)

        res._compute_attendance()
        return res

    @api.multi
    def write(self, vals):
        res = super(AccountAnalyticLine, self).write(vals)

        self._compute_attendance()
        return res

    def _compute_attendance(self):
        if self.user_id.employee_ids:
            employee = self.user_id.employee_ids[0]
            attendance = False
            attendances = self.env['hr.attendance'].search([('employee_id', '=', employee.id), ('date', '=', self.date)], order="check_in DESC")
            if attendances:
                if len(attendances.ids) > 1:
                    raise UserError('There is dupplicated data for your attendance at %s, please contact your administrator to fix dupplicated data' % self.date)
                else:
                    attendance = attendances[0]
            all_timesheet = self.search([('date', '=', self.date), ('user_id', '=', self.user_id.id), ('project_id', '!=', False)])
            all_time = all_timesheet.mapped("unit_amount") if all_timesheet else []
            all_time = sum(all_time)
            partner_id = employee.user_id.partner_id
            tz = pytz.timezone(employee.user_id.partner_id.tz) if partner_id else pytz.timezone(pytz.utc)

            if not attendance and all_timesheet:
                att_model = self.env['hr.attendance']
                # TODO: dont call like this
                working_time = employee.calendar_id
                check_in = False
                check_out = False
                if working_time:
                    rules = working_time.attendance_ids.filtered(
                        lambda r: int(r.dayofweek) == int(datetime.strptime(self.date, DEFAULT_SERVER_DATE_FORMAT).weekday()))
                    if rules:
                        plan_in = rules.mapped("hour_from")[0] if rules.mapped("hour_from") else False
                        check_in = tz.localize(datetime.strptime(str(self.date)[:10] + " " + att_model.float_to_time(plan_in) + ":00", DEFAULT_SERVER_DATETIME_FORMAT)) if plan_in else False
                        check_out = check_in + timedelta(hours=all_time) if all_time else False

                if not check_in:
                    check_in = tz.localize(datetime.strptime("%s 08:00:00" % str(self.date)[:10], DEFAULT_SERVER_DATETIME_FORMAT))
                    check_out = check_in + timedelta(hours=all_time) if all_time else False
                
                if check_in:
                        att_model.create({
                            'employee_id': employee.id,
                            'date': self.date,
                            'check_in': check_in.astimezone(pytz.utc).strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                            'check_out': check_out.astimezone(pytz.utc).strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                            'reason': "Auto reason from timesheet",
                            'reason_date': self.date,
                            'reason_status': 'accept',
                            'work_outside': employee.is_consultant,
                        })

            elif all_timesheet:
                vals = {
                    'reason': "Auto reason from timesheet",
                    'reason_date': self.date,
                    'reason_status': 'accept',
                    'work_outside': employee.is_consultant,
                }

                if not attendance.check_out:
                    check_in_date = datetime.strptime(attendance.check_in, DEFAULT_SERVER_DATETIME_FORMAT)
                    check_out_date = check_in_date + timedelta(hours=all_time)
                    vals['check_out'] = check_out_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                
                attendance.write(vals)