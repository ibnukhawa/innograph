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

    @http.route(['/hr/attendance/logging'], type='http', auth='none', methods=['POST'], csrf=False)
    def attendance_callback(self, finger_id=False, check_time=False, **post):
        res = {}
        if not finger_id or not check_time:
            res['success'] = False
            res['exception'] = "empty payload"
            return json.dumps(res)
        
        try:
            Attendance = request.env['hr.attendance'].sudo()
            res = Attendance.input_data(int(finger_id), check_time)
            return res
        except Exception, e:
            res['success'] = False
            res['exception'] = str(e[0] if e[0] else e)
            return json.dumps(res)

        return json.dumps(res)
