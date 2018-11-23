from datetime import datetime
from odoo import models, api
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
import pytz


class HrEmployee(models.Model):
    _inherit = "hr.attendance"

    def send_email_reason(self):
        if self:
            employee = self.employee_id
            coach = False
            if employee:
                tz = pytz.timezone(employee.user_id.tz) if employee.user_id.tz else pytz.utc
                coach = self.employee_id.coach_id
            else:
                tz = pytz.utc

            date_att = False
            if self.date:
                date_att = datetime.strptime(self.date, DEFAULT_SERVER_DATE_FORMAT)
                date_att = date_att.strftime("%d-%m-%Y")

            check_in = False
            if self.check_in:
                check_in = datetime.strptime(self.check_in, DEFAULT_SERVER_DATETIME_FORMAT)
                check_in = pytz.utc.localize(check_in).astimezone(tz)

            check_out = False
            if self.check_out:
                check_out = datetime.strptime(self.check_out, DEFAULT_SERVER_DATETIME_FORMAT)
                check_out = pytz.utc.localize(check_out).astimezone(tz)

            timesheet_hour = False
            if self.sheet_id and self.sheet_id.timesheet_ids:
                times = self.sheet_id.timesheet_ids.filtered(lambda r: r.date == self.date)
                timesheet_hour = self.float_to_time(sum(times.mapped('unit_amount')))

            context = {
                'coach': coach,
                'date_att': date_att if date_att else "-",
                'check_in': check_in.strftime("%H:%M") if check_in else "-",
                'check_out': check_out.strftime("%H:%M") if check_out else "-",
                'timesheet': timesheet_hour if timesheet_hour else "-",
            }
            email = self.env.ref('pqm_portal_attendance.email_attendance_reason')
            email.with_context(data=context).send_mail(self.id, force_send=True)

        print True

    def send_email_approval(self):
        if self:
            employee = self.employee_id
            if employee:
                tz = pytz.timezone(employee.user_id.tz) if employee.user_id.tz else pytz.utc
            else:
                tz = pytz.utc

            date_att = False
            if self.date:
                date_att = datetime.strptime(self.date, DEFAULT_SERVER_DATE_FORMAT)
                date_att = date_att.strftime("%d-%m-%Y")

            check_in = False
            if self.check_in:
                check_in = datetime.strptime(self.check_in, DEFAULT_SERVER_DATETIME_FORMAT)
                check_in = pytz.utc.localize(check_in).astimezone(tz)

            check_out = False
            if self.check_out:
                check_out = datetime.strptime(self.check_out, DEFAULT_SERVER_DATETIME_FORMAT)
                check_out = pytz.utc.localize(check_out).astimezone(tz)

            timesheet_hour = False
            if self.sheet_id and self.sheet_id.timesheet_ids:
                times = self.sheet_id.timesheet_ids.filtered(lambda r: r.date == self.date)
                timesheet_hour = self.float_to_time(sum(times.mapped('unit_amount')))

            context = {
                'manager': self.reason_manager_id.name,
                'date_att': date_att if date_att else "-",
                'check_in': check_in.strftime("%H:%M") if check_in else "-",
                'check_out': check_out.strftime("%H:%M") if check_out else "-",
                'timesheet': timesheet_hour if timesheet_hour else "-",
            }
            email = self.env.ref('pqm_portal_attendance.email_attendance_approval')
            email.with_context(data=context).send_mail(self.id, force_send=True)

