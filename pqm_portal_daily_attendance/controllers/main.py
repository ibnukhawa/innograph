# -*- coding:utf-8 -*-
"""modify customer db authentication mechanism"""
from odoo import http, SUPERUSER_ID
from odoo.http import request
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime, date, timedelta
from calendar import monthrange
import json
import pytz


class Home(http.Controller):

    # ideally, this route should be `auth="user"`
    @http.route('/web/attendance/realtime', type='http', auth="public")
    def get_attendance(self, **kw):
        user = request.env.user
        tz = pytz.timezone(user.tz) if user.tz else pytz.utc
        check_date = pytz.utc.localize(datetime.now()).astimezone(tz)
        domain = [
            ('date', '=', check_date.strftime(DEFAULT_SERVER_DATE_FORMAT)),
            ('auto_attendance', '=', False),
        ]
        lines = request.env['hr.attendance'].sudo().search(domain, order="check_in desc")
        pegawai_total = request.env['hr.employee'].sudo().search_count([])
        data = []
        for line in lines:
            tz = pytz.timezone(line.employee_id.user_id.tz) if line.employee_id.user_id.tz else pytz.utc
            check_in = datetime.strptime(line.check_in, DEFAULT_SERVER_DATETIME_FORMAT)
            check_in = pytz.utc.localize(check_in).astimezone(tz)            
            if check_in:
                data.append({
                    'name': line.employee_id.name,
                    'check_in': check_in.strftime('%H:%M:%S'),
                })

        return json.dumps({
                'chart': {
                    'pegawai_total': pegawai_total,
                },
                'tabel': {
                    'data': data,
                }
            })

    @http.route('/dailyattend', type='http', auth="public", website=True)
    def daily_attend(self, **kw):
        vals = {}
        today_list = []
        nextday_list = []
        user = request.env.user
        tz = pytz.timezone(user.tz) if user.tz else pytz.utc
        date_start = datetime.now().replace(hour=0, minute=0, second=0)
        date_stop = date_start + timedelta(days=1)
        date_start = tz.localize(date_start).astimezone(pytz.utc)
        date_stop = tz.localize(date_stop).astimezone(pytz.utc)
        leave_today = request.env['hr.holidays'].sudo().search([('state', '=', 'validate'), ('type', '=', 'remove'),
                                                                ('date_from', '<', date_stop.strftime(DEFAULT_SERVER_DATETIME_FORMAT)),
                                                                ('date_to', '>=', date_start.strftime(DEFAULT_SERVER_DATETIME_FORMAT))])

        leave_next = request.env['hr.holidays'].sudo().search([('state', '=', 'validate'), ('type', '=', 'remove'),
                                                               ('date_to', '>=', date_stop.strftime(DEFAULT_SERVER_DATETIME_FORMAT))])

        for leave in leave_today:
            from_tz = pytz.utc.localize(
                datetime.strptime(leave.date_from, DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(tz)
            to_tz = pytz.utc.localize(
                datetime.strptime(leave.date_to, DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(tz)

            today_list.append({
                'employee': leave.employee_id.name,
                'date_from': from_tz.strftime(DEFAULT_SERVER_DATE_FORMAT),
                'date_to': to_tz.strftime(DEFAULT_SERVER_DATE_FORMAT),
                'type': leave.holiday_status_id.name,
            })

        for leave in leave_next:
            from_tz = pytz.utc.localize(
                datetime.strptime(leave.date_from, DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(tz)
            to_tz = pytz.utc.localize(
                datetime.strptime(leave.date_to, DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(tz)

            nextday_list.append({
                'employee': leave.employee_id.name,
                'date_from': from_tz.strftime(DEFAULT_SERVER_DATE_FORMAT),
                'date_to': to_tz.strftime(DEFAULT_SERVER_DATE_FORMAT),
                'type': leave.holiday_status_id.name,
            })
        vals['today'] = today_list
        vals['next_day'] = nextday_list
        return request.render("pqm_portal_daily_attendance.daily_attendance_new", vals)