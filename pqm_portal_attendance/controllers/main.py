# -*- coding:utf-8 -*-
"""modify customer db authentication mechanism"""
from odoo import http, SUPERUSER_ID
from odoo.http import request
from datetime import datetime, date, timedelta
from calendar import monthrange
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
import pytz
import werkzeug
import json


class PQMAttendance(http.Controller):

    @http.route(['/my/workoutside/submit'], type='http', auth='user', website=True)
    def work_outside_submit(self, attendance_id=False, **post):
        if not attendance_id:
            request.session['success'] = False
            request.session['message'] = "Your action can't be processed, fill all required fields!"
            return werkzeug.utils.redirect('/my/attendance')

        try:
            attendance = request.env['hr.attendance'].browse(int(attendance_id))
            attendance.sudo().write({
                'work_outside': True,
            })
        except Exception, e:
            request.session['success'] = False
            request.session['message'] = str(e[0] if e[0] else e)
            return werkzeug.utils.redirect('/my/attendance')

        request.session['success'] = True
        request.session['message'] = 'the attendance record was successfully updated!'
        return werkzeug.utils.redirect('/my/attendance')

    @http.route(['/my/reason/approval'], type='http', auth="user", website=True)
    def my_reason_approval(self, attendance_id=False, status=False, **kw):
        if status not in ['accept', 'decline'] or not attendance_id:
            request.session['success'] = False
            request.session['message'] = "Your action can't be processed, fill all required fields!"
            return werkzeug.utils.redirect('/my/reason')

        attendance = request.env['hr.attendance'].sudo().browse(int(attendance_id))
        if not attendance:
            request.session['success'] = False
            request.session[
                'message'] = "Your action can't be processed, attendance data not found!"
            return werkzeug.utils.redirect('/my/reason')

        try:
            user = request.env.user
            attendance.write({
                'reason_status': status,
                'reason_manager_id': user.employee_ids.id,
            })
            attendance.send_email_approval()
        except Exception, e:
            request.session['success'] = False
            request.session['message'] = str(e[0] if e[0] else e)
            return werkzeug.utils.redirect('/my/reason')

        request.session['success'] = True
        if status == 'accept':
            request.session['message'] = 'the attendance reason was successfully accepted!'
        else:
            request.session['message'] = 'the attendance reason was successfully declined!'
        return werkzeug.utils.redirect('/my/reason')

    @http.route(['/my/reason/submit'], type='http', auth="user", website=True)
    def my_reason_submit(self, attendance_id=False, reason=False, date=False, employee_id=False,
                         check_in=False, check_out=False, **kw):
        if not reason or not date:
            request.session['success'] = False
            request.session['message'] = "Your action can't be processed, fill all required fields!"
            return werkzeug.utils.redirect('/my/attendance')

        user = request.env.user
        tz = pytz.timezone(user.tz) if user.tz else pytz.utc
        if attendance_id:
            attendance = request.env['hr.attendance'].sudo().browse(int(attendance_id))
            vals = {
                'reason': reason,
                'reason_date': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                'reason_status': 'open',
            }
            if not attendance.check_out:
                check_out = datetime.strptime("%s %s" % (date, check_out),
                                              DEFAULT_SERVER_DATETIME_FORMAT)
                check_out = tz.localize(check_out).astimezone(pytz.utc)
                vals['check_out'] = check_out.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
            try:
                attendance.write(vals)
                attendance.send_email_reason()
            except Exception, e:
                request.session['success'] = False
                request.session['message'] = str(e[0] if e[0] else e)
                return werkzeug.utils.redirect('/my/attendance')

        else:
            employee = request.env['hr.employee'].sudo().browse(int(employee_id))
            if not employee:
                request.session['success'] = False
                request.session['message'] = "Reason input failed, employee data not found!"
                return werkzeug.utils.redirect('/my/attendance')
            check_in = datetime.strptime("%s %s" % (date, check_in), DEFAULT_SERVER_DATETIME_FORMAT)
            check_in = tz.localize(check_in).astimezone(pytz.utc)
            check_out = datetime.strptime("%s %s" % (date, check_out),
                                          DEFAULT_SERVER_DATETIME_FORMAT)
            check_out = tz.localize(check_out).astimezone(pytz.utc)
            vals = {
                'employee_id': employee.id,
                'check_in': check_in.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                'check_out': check_out.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                'reason': reason,
                'reason_date': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                'reason_status': 'open',
            }
            try:
                attendance = request.env['hr.attendance'].sudo().create(vals)
                attendance.send_email_reason()
            except Exception, e:
                request.session['success'] = False
                request.session['message'] = str(e[0] if e[0] else e)
                return werkzeug.utils.redirect('/my/attendance')

        request.session['success'] = True
        request.session['message'] = 'Your reason successfully stored, wait for review!'
        return werkzeug.utils.redirect('/my/attendance')

    @http.route(['/my/reason'], type='http', auth="user", website=True)
    def my_reason(self, **kw):
        success = request.session.get('success', None)
        request.session['success'] = None
        message = request.session.get('message', None)
        request.session['message'] = None
        lines = []
        user = request.env.user
        if not user.employee_ids:
            success, message = False, 'Only employee account that can access data on this menu!'
        else:
            domain = [
                ('reason_status', '!=', False)
            ]
            datas = request.env['hr.attendance'].sudo().search(domain, order="date desc")
            for data in datas:
                if data.employee_id.coach_id:
                    if data.employee_id.coach_id.id == user.employee_ids.id:
                        status_text = dict(dict(data.fields_get())['reason_status']['selection'])[
                            data.reason_status]
                        status_reason_text = dict(dict(data.fields_get())['status']['selection'])[
                            data.status]
                        tz = pytz.utc
                        employee = data.employee_id
                        if employee:
                            tz = pytz.timezone(employee.user_id.tz) if employee.user_id.tz else pytz.utc

                        check_in = False
                        if data.check_in:
                            check_in = datetime.strptime(data.check_in, DEFAULT_SERVER_DATETIME_FORMAT)
                            check_in = pytz.utc.localize(check_in).astimezone(tz)
                            check_in = self.datetime_to_float(check_in)
                        check_in = data.float_to_time(check_in)

                        check_out = False
                        if data.check_out:
                            check_out = datetime.strptime(data.check_out, DEFAULT_SERVER_DATETIME_FORMAT)
                            check_out = pytz.utc.localize(check_out).astimezone(tz)
                            check_out = self.datetime_to_float(check_out)
                        check_out = data.float_to_time(check_out)

                        timesheet_hour = False
                        if data.sheet_id and data.sheet_id.timesheet_ids:
                            times = data.sheet_id.timesheet_ids.filtered(lambda r: r.date == data.date)
                            timesheet_hour = data.float_to_time(sum(times.mapped('unit_amount')))
                        lines.append({
                            'id': data.id,
                            'date': data.date,
                            'name': data.employee_id.name,
                            'in': check_in,
                            'out': check_out,
                            'timesheet': timesheet_hour,
                            'reason': data.reason,
                            'status': data.reason_status,
                            'status_text': status_text,
                            'status_reason_text': status_reason_text,
                        })

        res = {
            'lines': lines,
            'hide_sidebar': True,
            'success': success,
            'message': message
        }
        return request.render("pqm_portal_attendance.reason_approval", res)

    @http.route(['/my/attendance'], type='http', auth="user", website=True)
    def my_attendance(self, month=None, year=None, **kw):
        success = request.session.get('success', None)
        request.session['success'] = None
        message = request.session.get('message', None)
        request.session['message'] = None
        year = date.today().year if not year else int(year)
        month = date.today().month if not month else int(month)

        request.env.cr.execute(
            """SELECT * FROM (SELECT to_char(date, 'YYYY') as year from hr_attendance WHERE date IS NOT NULL GROUP BY date ORDER BY date ASC) AS main GROUP BY year""")
        list_year = [str(row[0]) for row in request.env.cr.fetchall()]
        list_year = [year] if len(list_year) < 1 else list_year
        list_month = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August',
                      'September', 'October', 'November', 'December']

        attendants = []
        employee = request.env['hr.employee'].sudo().search([('user_id', '=', request.env.user.id)])
        if employee:
            days = [date(year, month, day) for day in range(1, monthrange(year, month)[1] + 1)]
            tz = pytz.timezone(employee.user_id.tz) if employee.user_id.tz else pytz.utc
            date_today = pytz.utc.localize(datetime.now()).astimezone(tz)
            date_today = date(date_today.year, date_today.month, date_today.day)
            for row in days:
                today = True if row == date_today else False
                tomorrow = True if row > date_today else False
                attendance = {
                    'id': '',
                    'employee_id': employee.id,
                    'date': row.strftime(DEFAULT_SERVER_DATE_FORMAT),
                    'tomorrow': tomorrow,
                    'today': today,
                }

                rules = employee.calendar_id.attendance_ids.filtered(
                    lambda r: int(r.dayofweek) == int(row.weekday()))
                if rules:
                    attendance['rules'] = True
                    attendance['plan_in'] = request.env['hr.attendance'].float_to_time(rules.mapped('hour_from')[0])
                    attendance['plan_out'] = request.env['hr.attendance'].float_to_time(rules.mapped('hour_to')[0])

                domain = [
                    ('employee_id', '=', employee.id),
                    ('date', '=', attendance['date'])
                ]
                data = request.env['hr.attendance'].sudo().search(domain, order="id desc", limit=1)
                if data:
                    attendance['id'] = data.id
                    if data.working_time and data.working_time.attendance_ids:
                        rules = data.working_time.attendance_ids.filtered(
                            lambda r: int(r.dayofweek) == int(data.day_of_week))
                        if rules:
                            attendance['rules'] = True
                            attendance['plan_in'] = data.float_to_time(rules.mapped('hour_from')[0])
                            attendance['plan_out'] = data.float_to_time(rules.mapped('hour_to')[0])

                    check_in = False
                    if data.check_in:
                        check_in = datetime.strptime(data.check_in, DEFAULT_SERVER_DATETIME_FORMAT)
                        check_in = pytz.utc.localize(check_in).astimezone(tz)
                        check_in = self.datetime_to_float(check_in)
                    check_in = data.float_to_time(check_in)
                    attendance['actual_in'] = check_in

                    check_out = False
                    if data.check_out:
                        check_out = datetime.strptime(data.check_out,
                                                      DEFAULT_SERVER_DATETIME_FORMAT)
                        check_out = pytz.utc.localize(check_out).astimezone(tz)
                        check_out = self.datetime_to_float(check_out)
                    check_out = data.float_to_time(check_out)
                    attendance['actual_out'] = check_out

                    timesheet_hour = False
                    if data.sheet_id and data.sheet_id.timesheet_ids:
                        times = data.sheet_id.timesheet_ids.filtered(lambda r: r.date == data.date)
                        timesheet_hour = sum(times.mapped('unit_amount'))

                    status_text = dict(dict(data.fields_get())['status']['selection'])[data.status]

                    attendance['actual_work'] = data.float_to_time(data.worked_hours)
                    attendance['in_late'] = data.float_to_time(data.hour_late)
                    attendance['out_early'] = data.float_to_time(data.hour_early)
                    attendance['timesheet'] = data.float_to_time(timesheet_hour)
                    attendance['status'] = data.status
                    attendance['status_text'] = status_text
                    attendance['punishment'] = data.punishment_late
                    attendance['reason'] = data.reason
                    attendance['reason_status'] = data.reason_status
                    attendance['work_outside'] = data.work_outside
                    attendance['work_outside_text'] = "Dinas" if data.work_outside else "Non Dinas"

                attendants.append(attendance)

        respone = {
            'attendants': attendants,
            'year': year,
            'month': month,
            'list_month': list_month,
            'list_year': list_year,
            'hide_sidebar': True,
            'success': success,
            'message': message
        }
        return request.render("pqm_portal_attendance.my_attendance", respone)

    def datetime_to_float(self, value):
        if not value:
            return False
        return float(value.time().hour) + value.time().minute / 60.0 + value.time().second / 3600.0
