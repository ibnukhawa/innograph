# -*- coding:utf-8 -*-
"""modify customer db authentication mechanism"""
from odoo import http, SUPERUSER_ID, fields
from odoo.http import request
from datetime import datetime, date
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
import werkzeug
import pytz
from odoo.exceptions import ValidationError


class PQMLeaves(http.Controller):

    @http.route(['/leaves/approval/action'], type='http', auth="user", website=True)
    def leaves_approval_action(self, leave_id=False, status=False, note=False, **kw):
        user = request.env.user
        group_holiday_manager = request.env.ref('hr_holidays.group_hr_holidays_manager')
        holiday_manager = request.env['res.users'].search([('groups_id', 'in', [group_holiday_manager.id])])
        if user in holiday_manager:
            if status not in ['validate', 'refuse'] or not leave_id:
                request.session['success'] = False
                request.session['message'] = "Your action can't be processed, fill all required fields!"
                return werkzeug.utils.redirect('/leaves/approval')
            
            leave = request.env['hr.holidays'].browse(int(leave_id))
            if not leave:
                request.session['success'] = False
                request.session['message'] = "Your action can't be processed, leave data not found!"
                return werkzeug.utils.redirect('/leaves/approval')

            try:
                leave.write({
                    "report_note": note,
                })
                if status == 'validate':
                    leave.action_approve()
                else:
                    leave.action_refuse()
            except Exception, e:
                request.session['success'] = False
                request.session['message'] = str(e[0] if e[0] else e)
                return werkzeug.utils.redirect('/leaves/approval')

            request.session['success'] = True
            if status == 'validate':
                request.session['message'] = 'employee leave was successfully Validated!'
            else:
                request.session['message'] = 'employee leave was successfully Refused!'
        else:
            request.session['success'] = False
            request.session['message'] = "You cannot approve leave because of your account access restriction.<br/>Contact your administrator!"
        return werkzeug.utils.redirect('/leaves/approval')

    @http.route(['/leaves/approval'], type='http', auth="user", website=True)
    def leaves_approval(self, **kw):
        user = request.env.user
        group_holiday_manager = request.env.ref('hr_holidays.group_hr_holidays_manager')
        holiday_manager = request.env['res.users'].search([('groups_id', 'in', [group_holiday_manager.id])])
        if user in holiday_manager:
            success = request.session.get('success', None)
            request.session['success'] = None 
            message = request.session.get('message', None)
            request.session['message'] = None
            lines = []
            user = request.env.user
            if not user.employee_ids:
                success, message = False, 'Only employee account that can access data on this menu!'
            else:
                domain = [('state', 'not in', ['draft', 'cancel']), ('type', '=', 'remove')]
                leaves = request.env['hr.holidays'].sudo().search(domain, order="date_from desc")
                for leave in leaves:
                    if leave.coach_id and leave.coach_id.id == user.employee_ids.id:
                        status_text = dict(dict(leave.fields_get())['state']['selection'])[leave.state]
                        lines.append({
                            'id': leave.id,
                            'name': leave.employee_id.name,
                            'description': leave.name,
                            'leave_type': leave.holiday_status_id.name,
                            'date_from': leave.date_from,
                            'date_to': leave.date_to,
                            'duration': leave.number_of_days_temp,
                            'note': leave.report_note,
                            'status': leave.state,
                            'status_text': status_text,
                        })

            response = {
                'lines': lines,
                'hide_sidebar': True,
                'success': success,
                'message': message,
            }
            return request.render("pqm_portal_leave.leaves_approval", response)
        else:
            return werkzeug.utils.redirect("/my/leaves")

    @http.route(['/my/leaves'], type='http', auth="user", website=True)
    def my_leaves(self, **kw):
        user = request.env.user
        group_holiday_user = request.env.ref('base.group_user')
        holiday_user = request.env['res.users'].search([('groups_id', 'in', [group_holiday_user.id])])
        if user in holiday_user:
            success = request.session.get('success', None)
            request.session['success'] = None 
            message = request.session.get('message', None)
            request.session['message'] = None
            leaves = request.env['hr.holidays'].sudo().search([('user_id', '=', request.env.user.id)], order="date_from desc")
            leave_type = request.env['hr.holidays.status'].sudo().search([])
            types = []
            # query_list = []
            if user.employee_ids:
                # TODO: fix this query.
                # request.env.cr.execute("""SELECT t.name AS name, SUM(number_of_days) AS remaining_days, 
                #                         SUM(case when l.number_of_days > 0 then l.number_of_days else 0 end) AS days,
                #                         SUM(case when l.number_of_days < 0 then l.number_of_days_temp else 0 end) AS total_days
                #                         FROM hr_holidays l
                #                         LEFT JOIN hr_holidays_status t ON (l.holiday_status_id=t.id)
                #                         WHERE l.employee_id='%s'
                #                         AND l.state='validate'
                #                         GROUP BY t.name""" % request.env.user.employee_ids.id)
                # query_list = request.env.cr.fetchall()
                tz = user.partner_id.tz or pytz.utc
                for leave in leave_type:
                    domain = [
                        ('employee_id', '=', user.employee_ids.id),
                        ('holiday_status_id', '=', leave.id),
                        ('type', '=', 'add'),
                        ('state', '=', 'validate')
                    ]
                    lines = request.env['hr.holidays'].sudo().search(domain)
                    allocation = sum(line.number_of_days_temp for line in lines)

                    domain = [
                        ('employee_id', '=', user.employee_ids.id), 
                        ('holiday_status_id', '=', leave.id),
                        ('type', '=', 'remove'), 
                        ('state', '=', 'validate')
                    ]
                    lines = request.env['hr.holidays'].sudo().search(domain)
                    total = sum(line.number_of_days for line in lines)

                    remaining = allocation + total
                    if allocation != 0.0 or total != 0.0:
                        if not leave.show_deficit:
                            remaining = 0.0 if remaining < 0.0 else remaining
                        types.append({
                            'name': leave.name,
                            'days': '%.2f' % allocation,
                            'total_days': '%.2f' % abs(total),
                            'remaining_days': '%.2f' % remaining,
                        })

            data_leaves = []
            for rec in leaves:
                l = {}
                date_from = fields.Datetime.to_string(fields.Datetime.context_timestamp(rec.with_context(tz=tz),
                                                                                        fields.Datetime.from_string(rec.date_from))) if rec.date_from else ""
                date_to = fields.Datetime.to_string(fields.Datetime.context_timestamp(rec.with_context(tz=tz),
                                                                                      fields.Datetime.from_string(rec.date_to))) if rec.date_to else ""
                l['holiday_status_id'] = rec.holiday_status_id.name
                l['date_from'] = date_from[:16]
                l['date_to'] = date_to[:16]
                l['number_of_days_temp'] = rec.number_of_days_temp
                l['name'] = rec.name
                l['state'] = rec.state
                l['state_text'] = dict(dict(rec.fields_get())['state']['selection'])[rec.state]
                l['note'] = rec.report_note
                data_leaves.append(l)

            data_types = []
            for rec in types:
                t = {}
                t['name'] = rec['name']
                t['remaining_days'] = rec['remaining_days'] if rec['remaining_days'] > 0 else 0
                t['days'] = rec['days']
                t['total_days'] = rec['total_days']
                data_types.append(t)

            response = {
                'leaves': data_leaves,
                'types': data_types,
                'leave_type': leave_type,
                'hide_sidebar': True,
                'success': success,
                'message': message,
            }
            return request.render("pqm_portal_leave.my_leaves", response)
        else:
            return werkzeug.utils.redirect("/my/home")

    @http.route('/my/leaves/submit', type='http', auth='user', website=True)
    def my_leaves_submit(self, name=False, date_from=False, date_to=False, duration=False, holiday_status_id=False, **kw):
        user = request.env.user
        group_holiday_user = request.env.ref('base.group_user')
        holiday_user = request.env['res.users'].search([('groups_id', 'in', [group_holiday_user.id])])
        if user in holiday_user:
            if not name or not date_from or not date_to or not duration or not holiday_status_id:
                request.session['success'] = False
                request.session['message'] = "required field is empty!"
                return werkzeug.utils.redirect("/my/leaves")

            employee = request.env.user.employee_ids
            tz = pytz.timezone(request.env.user.tz) or pytz.utc

            date_from = tz.localize(datetime.strptime(date_from, DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(pytz.utc)
            date_to = tz.localize(datetime.strptime(date_to, DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(pytz.utc)
            date_from_str = date_from.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
            date_to_str = date_to.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
            domain = [
                ('date_from', '<=', date_to_str),
                ('date_to', '>=', date_from_str),
                ('employee_id', '=', employee.id),
                ('state', 'not in', ['cancel', 'refuse'])
            ]
            nholidays = request.env['hr.holidays'].sudo().search_count(domain)
            if nholidays:
                request.session['success'] = False
                request.session['message'] = "You can not have 2 leaves that overlaps on same day!"
                return werkzeug.utils.redirect("/my/leaves")

            if float(duration) <= 0.0:
                request.session['success'] = False
                request.session['message'] = "You must set duration of your leave!"
                return werkzeug.utils.redirect("/my/leaves")

            data = {
                'name': name,
                'holiday_status_id': holiday_status_id,
                'employee_id': employee.id,
                'date_from': date_from,
                'date_to': date_to,
                'number_of_days_temp': duration,
            }

            try:
                holiday = request.env['hr.holidays'].create(data)
                holiday.action_message_leave_request()
            except ValidationError, e:
                domain = [
                    ('holiday_status_id', '=', int(holiday_status_id)),
                    ('employee_id', '=', employee.id),
                    ('date_from', '=', date_from_str),
                    ('date_to', '=', date_to_str),
                ]
                leave = request.env['hr.holidays'].sudo().search(domain, order="id desc", limit=1)
                if leave: 
                    leave.unlink()
                request.session['success'] = False
                request.session['message'] = str(e[0] if e[0] else e)
                return werkzeug.utils.redirect("/my/leaves")
            except Exception, e:
                request.session['success'] = False
                request.session['message'] = str(e[0] if e[0] else e)
                return werkzeug.utils.redirect("/my/leaves")
            
            request.session['success'] = True 
            request.session['message'] = "Your leave created successfully!"
            return werkzeug.utils.redirect("/my/leaves")
        else:
            request.session['success'] = False
            request.session['message'] = "You cannot request leave because of your account access restriction.<br/>Contact your administrator!"
        return werkzeug.utils.redirect("/my/leaves")
