# -*- coding:utf-8 -*-
"""modify customer db authentication mechanism"""
from odoo import http, SUPERUSER_ID
from odoo.http import request
from datetime import datetime, date
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
import werkzeug
from odoo.exceptions import ValidationError
from cStringIO import StringIO
from PIL import Image, ImageOps, ImageDraw


class PQMEmployees(http.Controller):

    def make_square(self, im, min_size=200):
        x, y = im.size
        size = max(min_size, x, y)
        im.paste(im, ((size - x) / 2, (size - y) / 2))
        return im

    @http.route(['/my/profiles'], type='http', auth="user", website=True)
    def my_profiles(self, **kw):
        employee = request.env.user.employee_ids
        is_employee = True if employee else False
        success = request.session.get('success', None)
        request.session['success'] = None 
        message = request.session.get('message', None)
        request.session['message'] = None
        employee_obj = request.env['hr.employee'].sudo().search([('id', '=', employee.id)])
        country_obj = request.env['res.country']
        partner_obj = request.env['res.partner']
        partner_bank_obj = request.env['res.partner.bank']
        gender_obj = dict(employee_obj.fields_get()['gender']['selection'])
        marital_obj = dict(employee_obj.fields_get()['marital']['selection'])
        emergency_obj = request.env['hr.emergency.contact'].sudo().search([('employee_obj', '=', employee.id)])
        academic_obj = request.env['hr.academic'].sudo().search([('employee_id', '=', employee.id)])
        certification_obj = request.env['hr.certification'].sudo().search([('employee_id', '=', employee.id)])
        
        employees = []
        for rec in employee_obj:
            data = {}
            data['name'] = rec['name']
            data['identification_id'] = rec['identification_id']
            data['passport_id'] = rec['passport_id']
            data['country_id'] = rec['country_id'].id
            data['bank_account_id'] = rec['bank_account_id'].id
            data['birthday'] = rec['birthday']
            data['place_of_birth'] = rec['place_of_birth']
            data['age'] = rec['age']
            data['gender'] = rec['gender']
            data['marital'] = rec['marital']
            data['children'] = rec['children']
            data['address_home_id'] = rec['address_home_id'].id
            data['personal_mobile'] = rec['personal_mobile']
            # image compression using PIL
            # From base64 to PIL
            image_string = StringIO(rec['image'].decode('base64'))
            im = Image.open(image_string)
            im.thumbnail((200, 200), Image.ANTIALIAS)
            im = self.make_square(im)
            # From PIL to base64
            output = StringIO()
            im.save(output, format='PNG')
            im_data = output.getvalue()
            data['image'] = 'data:image/png;base64,' + im_data.encode('base64')
            employees.append(data)

        response = {
            'employees': employees,
            'country_obj': country_obj.sudo().search([]),
            'partner_obj': partner_obj.sudo().search([]),
            'partner_bank_obj': partner_bank_obj.sudo().search([]),
            'gender_obj': gender_obj,
            'marital_obj': marital_obj,
            'emergency_obj': emergency_obj,
            'academic_obj': academic_obj,
            'certification_obj': certification_obj,
            'hide_sidebar': True,
            'success': success,
            'message': message,
            'is_employee': is_employee,
        }
        return request.render("pqm_portal_cv.my_profiles", response)

    @http.route('/my/profiles/submit', type='http', auth='user', website=True)
    def my_profile_submit(self, **post):
        
        employee = request.env.user.employee_ids
        data_employee = {
            'identification_id': post['identification_id'],
            'country_id': post['country_id'],
            'passport_id': post['passport_id'],
            'birthday': post['birthday'],
            'place_of_birth': post['place_of_birth'],
            'age': post['age'],
            'personal_mobile': post['personal_mobile'],
            'gender': post['gender'],
            'marital': post['marital'],
            'children': post['children'],
        }

        request.env['hr.employee'].sudo().search([('id', '=', employee.id)]).write(data_employee)
        
        return werkzeug.utils.redirect("/my/profiles")

    @http.route('/my/profiles/submit/emergency', type='http', auth='user', website=True)
    def my_profile_submit_emergency(self, **post):

        employee = request.env.user.employee_ids

        if post.get('action') not in ['add', 'save', 'remove']:
            request.session['success'] = False
            request.session['message'] = "required field is empty!"
            return werkzeug.utils.redirect("/my/profiles")

        new_emergency = {
            'employee_obj': employee.id,
            'number': post.get('new_emergency_number', False),
            'relation': post.get('new_emergency_relation', False),
        }

        data_emergency = {
            'number': post.get('emergency_number', False),
            'relation': post.get('emergency_relation', False),
        }

        if post.get('action') == 'add':
            request.env['hr.emergency.contact'].sudo().create(new_emergency)

        if post.get('action') == 'save':
            request.env['hr.emergency.contact'].sudo().search([('id', '=', post['emergency_id'])]).write(data_emergency)

        if post.get('action') == 'remove':
            request.env['hr.emergency.contact'].sudo().search([('id', '=', post['emergency_id'])]).unlink()
        
        return werkzeug.utils.redirect("/my/profiles")

    @http.route('/my/profiles/submit/academic', type='http', auth='user', website=True)
    def my_profile_submit_academic(self, **post):

        employee = request.env.user.employee_ids

        if post.get('action') not in ['add', 'save', 'remove']:
            request.session['success'] = False
            request.session['message'] = "required field is empty!"
            return werkzeug.utils.redirect("/my/profiles")

        new_academic = {
            'employee_id': employee.id,
            'name': post.get('new_academic_name', False),
            'start_date': post.get('new_academic_start', False),
            'end_date': post.get('new_academic_end', False),
            'partner_id': post.get('new_partner_id', False),
            'diploma': post.get('new_diploma', False),
            'study_field': post.get('new_study_field', False),
        }

        data_academic = {
            'name': post.get('name', False),
            'start_date': post.get('start_date', False),
            'end_date': post.get('end_date', False),
            'partner_id': post.get('partner_id', False),
            'diploma': post.get('diploma', False),
            'study_field': post.get('study_field', False),
        }

        if post.get('action') == 'add':
            request.env['hr.academic'].sudo().create(new_academic)

        if post.get('action') == 'save':
            request.env['hr.academic'].sudo().search([('id', '=', post['academic_id'])]).write(data_academic)

        if post.get('action') == 'remove':
            request.env['hr.academic'].sudo().search([('id', '=', post['academic_id'])]).unlink()
        
        return werkzeug.utils.redirect("/my/profiles")

    @http.route('/my/profiles/submit/certification', type='http', auth='user', website=True)
    def my_profile_submit_certification(self, **post):

        employee = request.env.user.employee_ids

        if post.get('action') not in ['add', 'save', 'remove']:
            request.session['success'] = False
            request.session['message'] = "required field is empty!"
            return werkzeug.utils.redirect("/my/profiles")

        new_certification = {
            'employee_id': employee.id,
            'name': post.get('new_certification_name', False),
            'certification': post.get('new_certification_number', False),
            'start_date': post.get('new_certification_start', False),
            'end_date': post.get('new_certification_end', False),
            'partner_id': post.get('new_partner_id', False),
        }

        data_certification = {
            'name': post.get('certification_name', False),
            'certification': post.get('certification_number', False),
            'start_date': post.get('certification_start_date', False),
            'end_date': post.get('certification_end_date', False),
            'partner_id': post.get('partner_id', False),
        }

        if post.get('action') == 'add':
            request.env['hr.certification'].sudo().create(new_certification)

        if post.get('action') == 'save':
            request.env['hr.certification'].sudo().search([('id', '=', post['certification_id'])]).write(data_certification)

        if post.get('action') == 'remove':
            request.env['hr.certification'].sudo().search([('id', '=', post['certification_id'])]).unlink()
        
        return werkzeug.utils.redirect("/my/profiles")