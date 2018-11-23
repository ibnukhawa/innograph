import pytz
import json
from datetime import date, datetime, timedelta
from odoo import fields, api, models, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo.models import BaseModel

class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    date = fields.Date()
    day_of_month = fields.Integer()
    day_of_week = fields.Integer()
    working_time = fields.Many2one('resource.calendar', related="employee_id.calendar_id")
    hour_late = fields.Float()
    hour_early = fields.Float()
    status = fields.Selection([
        ('check_out_empty', 'Check Out Empty'),
        ('check_in_late', 'Check In Late'),
        ('check_out_early', 'Check Out Early'),
        ('in_late_out_early', 'Check In Late and Check Out Early'),
        ('normal', 'Normal')
    ], default='check_out_empty')
    punishment_late = fields.Char()
    reason = fields.Char()
    reason_date = fields.Datetime()
    reason_status = fields.Selection([
        ('open', 'Waiting'), 
        ('accept', 'Accepted'),
        ('decline', 'Declined')])
    reason_manager_id = fields.Many2one(comodel_name='hr.employee')
    plan_in = fields.Float('Plan IN')
    plan_out = fields.Float('Plan OUT')
    work_outside = fields.Boolean()
    auto_attendance = fields.Boolean()

    @api.constrains('check_in', 'check_out', 'employee_id')
    def _check_validity(self):
        for attendance in self:
            user = attendance.employee_id.user_id
            tz = pytz.timezone(user.tz) if user.tz else pytz.utc
            check_in = datetime.strptime(attendance.check_in, DEFAULT_SERVER_DATETIME_FORMAT)
            check_date = pytz.utc.localize(check_in).astimezone(tz)
            last_attendance = self.env['hr.attendance'].search([
                ('employee_id', '=', attendance.employee_id.id),
                ('date', '=', check_date),
                ('id', '!=', attendance.id),
            ], order='check_in desc', limit=1)
            if last_attendance:
                raise ValidationError(_("Cannot create new attendance record for %(empl_name)s, the employee was already checked in") % {
                    'empl_name': attendance.employee_id.name_related
                })

    def reason_approve(self):
        status = self._context.get('status', False)
        if status:
            self.write({
                'reason_status': status,
                'reason_manager_id': self.env.user.employee_ids.id,
            })
        return True

    def _check(self):
        return True

    def _get_day_week_month(self, vals):
        values = {}
        user = self.employee_id.user_id
        tz = pytz.timezone(user.tz) if user.tz else pytz.utc
        check_in = vals.get('check_in') and vals.get('check_in') or self.check_in

        if check_in:
            check_in = datetime.strptime(check_in, DEFAULT_SERVER_DATETIME_FORMAT)
            check_in = pytz.utc.localize(check_in).astimezone(tz)
            values.update({'date':  check_in.strftime(DEFAULT_SERVER_DATE_FORMAT)})
            values.update({'day_of_month': check_in.day})
            values.update({'day_of_week': check_in.weekday()})
        return values

    def _get_late_early_hour(self, vals):
        values = {}

        user = self.employee_id.user_id
        tz = pytz.timezone(user.tz) if user.tz else pytz.utc

        check_in = vals.get('check_in') and vals.get('check_in') or self.check_in
        check_out = vals.get('check_out') and vals.get('check_out') or self.check_out
        hour_from = vals.get('plan_in') and vals.get('plan_in') or self.plan_in
        hour_to = vals.get('plan_out') and vals.get('plan_out') or self.plan_out

        if check_in and hour_from:
            time_in = pytz.utc.localize(
                datetime.strptime(check_in, DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(
                tz).time()
            time_in = time_in.hour + time_in.minute / 60.0 + time_in.second / 3600.0
            hour_late = time_in - hour_from if time_in - hour_from >= 0.0 else 0.0
            values.update({'hour_late': hour_late})

        if check_out and hour_to:
            time_out = pytz.utc.localize(
                datetime.strptime(check_out, DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(
                tz).time()
            time_out = time_out.hour + time_out.minute / 60.0 + time_out.second / 3600.0
            hour_early = hour_to - time_out if hour_to - time_out >= 0.0 else 0.0
            values.update({'hour_early': hour_early})
        return values

    @api.multi
    def write(self, values):
        for attendance in self:
            # Handle Date
            days = attendance._get_day_week_month(values)
            values.update(days)

            # Hadle hours
            hours = attendance._get_late_early_hour(values)
            values.update(hours)

            # Handle punishment
            punishment = attendance.check_punishment(values)
            values.update(punishment)

        res = super(HrAttendance, self).write(values)
        return res

    @api.model
    def create(self, vals):
        # default auto_attendance = True, except calling create with False as auto_attendance value
        if 'auto_attendance' not in vals:
            vals['auto_attendance'] = True
        res = False
        try:
            res = super(HrAttendance, self).create(vals)
            res.set_plan_hour()
            res.write({})
        except UserError, e:
            if e.name == "You can not enter an attendance in a submitted timesheet. Ask your manager to reset it before adding attendance.":
                res = self.create_override(vals)
                res.set_plan_hour()
                res.write({})
        return res

    def create_override(self, vals):
        return BaseModel.create(self, vals)

    def set_plan_hour(self):
        working_time = self.working_time

        if working_time:
            rules = working_time.attendance_ids.filtered(lambda r: int(r.dayofweek) == int(self.day_of_week))
            if rules:
                self.plan_in = rules.mapped("hour_from")[0] if rules.mapped("hour_from") else False
                self.plan_out = rules.mapped("hour_to")[0] if rules.mapped("hour_to") else False

    @api.model
    def init_plan_hour(self):
        for attendant in self.search(["|", ("plan_in", "=", False), ("plan_out", "=", False)]):
            attendant.set_plan_hour()

    def check_punishment(self, vals):
        resource = False
        if vals.get('working_time'):
            resource = self.env['resource.calendar'].browse(vals.get('working_time'))

        resource = resource and resource or self.working_time
        rules_temp = resource.late_ids
        rules = rules_temp.sorted(key=lambda k: k.minutes)

        hour_late = vals.get('hour_late', self.hour_late)
        hour_early = vals.get('hour_early', self.hour_early)
        reason_status = vals.get('reason_status', self.reason_status)

        res = {}
        # Check check in late
        is_late = False
        if rules:
            counter = 1
            for rule in rules:
                if 0.0 < hour_late <= rule.minutes or counter == len(rules):
                    is_late = True
                    res['punishment_late'] = rule.punishment
                    res['status'] = "check_in_late"
                    break
                counter = counter + 1
        else:
            if hour_late > 0:
                is_late = True
                res['punishment_late'] = False
                res['status'] = "check_in_late"

        if hour_late <= 0.0:
            is_late = False
            res['punishment_late'] = False
            res['status'] = "normal"

        # if check out is empty
        check_out = vals.get('check_out') if vals.get('check_out', False) else self.check_out
        if not check_out:
            res['status'] = "check_out_empty"

        # Check check out early
        is_early = False
        if hour_early > 0.0:
            is_early = True
            res['status'] = "check_out_early"

        # Check double punishment
        if is_late and is_early:
            res['status'] = "in_late_out_early"

        # if reason accepted
        if reason_status and reason_status == 'accept':
            res['punishment_late'] = False
            res['status'] = "normal"

        return res

    @api.model
    def input_data(self, finger_id, check_time):
        respone = {}
        try:
            employee = self.env['hr.employee'].search([('finger_id', '=', finger_id)])
            try:
                tz = pytz.timezone(employee.user_id.partner_id.tz)
            except Exception, e:
                raise Exception("User Time Zone Undefined")
            datetime_check = datetime.strptime(check_time, DEFAULT_SERVER_DATETIME_FORMAT)
            datetime_tz = tz.localize(datetime_check)
            datetime_utc = datetime_tz.astimezone(pytz.utc)
            date_string = datetime_check.date().strftime(DEFAULT_SERVER_DATE_FORMAT)
            datetime_utc_string  = datetime_utc.strftime(DEFAULT_SERVER_DATETIME_FORMAT)

            attendance = self.env['hr.attendance'].search(
                [('employee_id', '=', employee.id), ('date', '=', date_string)])

            if attendance and employee and datetime_check:
                if attendance.check_in and attendance.check_out:
                    if datetime_utc_string > attendance.check_out:
                        attendance.write(
                            {'check_out': datetime_utc_string})
                    elif datetime_utc_string < attendance.check_in:
                        attendance.write(
                            {'check_in': datetime_utc_string})
                elif attendance.check_in:
                    if datetime_utc_string < attendance.check_in:
                        check_temp = attendance.check_in
                        attendance.write(
                            {'check_in': datetime_utc_string,
                             'check_out': check_temp})
                    elif datetime_utc_string > attendance.check_in:
                        attendance.write(
                            {'check_out': datetime_utc_string})
            elif employee and datetime_check:
                self.env['hr.attendance'].create({
                    "employee_id": employee.id,
                    "check_in": datetime_utc_string,
                    "date": date_string,
                    "auto_attendance": False})
            respone['success'] = True
        except Exception, e:
            respone['success'] = False
            respone['exception'] = str(e)
        return json.dumps(respone)

    @api.depends('employee_id', 'check_in', 'check_out', 'sheet_id_computed.date_to',
                 'sheet_id_computed.date_from', 'sheet_id_computed.employee_id')
    def _compute_sheet(self):
        for attendance in self:
            corresponding_sheet = self.env['hr_timesheet_sheet.sheet'].search(
                [('date_to', '>=', attendance.check_in), ('date_from', '<=', attendance.check_in),
                 ('employee_id', '=', attendance.employee_id.id),
                 ('state', 'in', ['draft', 'new', 'confirm'])], limit=1)
            if corresponding_sheet:
                attendance.sheet_id_computed = corresponding_sheet[0]
                attendance.sheet_id = corresponding_sheet[0]

    @api.model
    def float_to_time(self, value):
        if not value:
            return False
        factor = value < 0 and -1 or 1
        val = abs(value)
        hour = factor * int(val)
        minutes = int(round((val % 1) * 60))
        minutes = minutes - 1 if minutes == 60 else minutes
        return "%02d:%02d" % (hour, minutes)