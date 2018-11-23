# -*- coding:utf-8 -*-
""" X """
from odoo import http, SUPERUSER_ID
from odoo.http import request
from datetime import datetime, date
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from odoo.addons.website_event.controllers.main import WebsiteEventController
from odoo.addons.website.models.website import slug
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from cStringIO import StringIO
import werkzeug
import base64
import qrcode
import pytz

class EventCoreController(WebsiteEventController):

    @http.route(['/event/attachment/<int:id>/download'], type='http', auth='public')
    def download_attachment(self, id):
        attachment = request.env['ir.attachment'].sudo().browse(id)
        if not attachment or attachment.res_model != 'event.event':
            return request.not_found()

        if attachment.url:
            return request.redirect(attachment.url)
        elif attachment.datas:
            data = StringIO(base64.b64decode(attachment.datas))
            return http.send_file(data, filename=attachment.name, as_attachment=True)
        else:
            return request.not_found()

    @http.route()
    def events(self, page=1, step=12, **searches):
        res = super(EventCoreController, self).events(page, **searches)
        vals = res.qcontext
        tz = pytz.timezone('Asia/Jakarta')
        
        # pqm core modification
        success = request.session.get('success', None)
        request.session['success'] = None
        message = request.session.get('message', None)
        request.session['message'] = None

        # Get event type list
        Event = request.env['event.event'].sudo()
        EventType = request.env['event.type'].sudo()
        EventTarget = request.env['event.target'].sudo()
        ResPartner = request.env['res.partner'].sudo()
        Category = request.env['project.sme'].sudo()
        SubCategory = request.env['project.sub.sme'].sudo()

        types = EventType.search([])
        facilitators = ResPartner.search([('is_facilitator', '=', True)])
        event_categories = Event.search([('project_sme_id', '!=', False)])
        categories = event_categories.mapped('project_sme_id')
        event_targets = EventTarget.search([])
        year_field = Event.search_read([], fields=['date_begin', 'date_end'])
        year_list = [year.get('date_begin', "")[:4] for year in year_field]
        year_list += [year.get('date_end', "")[:4] for year in year_field]
        year = [int(x) for x in set(year_list) if x.isdigit()]
        if year:
            year = zip(year, [str(x) for x in year])
        else:
            year = [(date.today().year, str(date.today().year))]

        step = int(step)
        selected_type = searches.get('type', 'all')
        selected_type = int(selected_type) if selected_type != 'all' else False
        selected_facilitator = searches.get('facilitator', 'all')
        selected_facilitator = int(selected_facilitator) if selected_facilitator != 'all' else False
        selected_category = searches.get('category', 'all')
        selected_category = int(selected_category) if selected_category != 'all' else False
        selected_sub_category = searches.get('sub_category', 'all')
        selected_sub_category = int(selected_sub_category) if selected_sub_category != 'all' else False
        selected_year = searches.get('year', 'upcoming')
        if selected_year != 'all' and selected_year != 'upcoming':
            selected_year = int(selected_year)
        elif selected_year == 'all':
            selected_year = False

        if selected_category:
            sub_categories = Event.search([('project_sme_id', '=', selected_category), ('project_sub_sme_id', '!=', False)])
        else:
            sub_categories = Event.search([('project_sub_sme_id', '!=', False)])
        sub_categories = sub_categories.mapped('project_sub_sme_id')

        prev_category = request.session.get('prev_category', False)
        if prev_category != selected_category:
            request.session['prev_category'] = selected_category
            selected_sub_category == False

        keyword = searches.get('keyword', '').strip()

        # Generate event domain
        events_domain = [('state', '=', 'confirm'), ('website_published', '=', True)]
        if selected_type:
            events_domain.append(['event_type_id', '=', selected_type])
        # if selected_facilitator:
        #     events_domain.append(['facilitator_ids', 'in', [selected_facilitator]])
        if selected_category:
            events_domain.append(['project_sme_id', '=', selected_category])
        if selected_sub_category:
            events_domain.append(['project_sub_sme_id', '=', selected_sub_category])
        if keyword:
            events_domain.append(['name', 'ilike', keyword])
        if selected_year == 'upcoming':
            today = datetime.now()
            today_utc = tz.localize(today).astimezone(pytz.utc)
            events_domain += [
                ('date_end', '>=', today_utc.strftime(DEFAULT_SERVER_DATETIME_FORMAT))]
        elif selected_year:
            begin_year = tz.localize(datetime(day=1, month=1, year=selected_year)).astimezone(pytz.utc)
            end_year = tz.localize(datetime(day=1, month=1, year=selected_year+1)).astimezone(pytz.utc)
            events_domain += [('date_begin', '<=', end_year.strftime(DEFAULT_SERVER_DATETIME_FORMAT)),
                              ('date_end', '>=', begin_year.strftime(DEFAULT_SERVER_DATETIME_FORMAT))]

        events = Event.search(events_domain)
        if selected_facilitator:
            events = events.filtered(lambda r: selected_facilitator in [x.partner_id.id for x in r.facilitator_ids])
        events_count = len(events.ids)
        pager = False
        mode = searches.get('mode', 'card')
        if mode == 'card':
            pager = request.website.pager(
                url = "/event",
                url_args = {
                    'mode': searches.get('mode', 'card'),
                    'type': searches.get('type'),
                    'facilitator': searches.get('facilitator'),
                    'category': searches.get('category'),
                    'sub_category': searches.get('sub_category'),
                    'keyword': searches.get('keyword'),
                    'year': searches.get('year', 'upcoming'),
                    'step': step
                },
                total = events_count,
                page = page,
                step = step,
                scope = 5
            )

            events = Event.search(events_domain, limit=step, offset=pager['offset'])
            if selected_facilitator:
                events = events.filtered(lambda r: selected_facilitator in [x.partner_id.id for x in r.facilitator_ids])

        vals['success'] = success
        vals['message'] = message
        vals['mode'] = mode
        vals['types'] = types
        vals['categories'] = categories
        vals['sub_categories'] = sub_categories
        vals['facilitators'] = facilitators
        vals['year'] = year
        vals['selected_type'] = selected_type
        vals['selected_facilitator'] = selected_facilitator
        vals['selected_category'] = selected_category
        vals['selected_sub_category'] = selected_sub_category
        vals['selected_year'] = selected_year
        vals['keyword'] = keyword
        vals['events'] = events
        vals['event_targets'] = event_targets
        vals['pager'] = pager
        vals['months'] = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        vals['step'] = step

        res.qcontext = vals
        return res

    @http.route()
    def event_register(self, event, **post):
        res = super(EventCoreController, self).event_register(event, **post)
        
        success = request.session.get('success', None)
        request.session['success'] = None 
        message = request.session.get('message', None)
        request.session['message'] = None

        res.qcontext['success'] = success
        res.qcontext['message'] = message
        res.qcontext['event'] = res.qcontext['event'].sudo()
        return res
    
    @http.route(['/event/<model("event.event"):event>/comment'], type='http', auth='public', website=True)
    def event_comment(self, event, **post):
        if not event:
            return request.not_found()

        user = request.env.user
        if not user:
            request.session['success'] = False
            request.session['message'] = 'User not found, please login.'
            return request.redirect('/event/%s/register' % slug(event))
        
        if not post.get('comment'):
            request.session['success'] = False
            request.session['message'] = 'Comment is empty, fill all required fields.'
            return request.redirect('/event/%s/register' % slug(event))

        vals = {
            'event_id': event.id,
            'user_id': user.id,
            'comment': post.get('comment', ''),
        }

        event.sudo().write({'comment_ids': [(0, 0, vals)]})
        request.session['success'] = True
        request.session['message'] = 'Comment successfully send, check your email for reply.'
        return request.redirect('/event/%s/register' % slug(event))

    @http.route(['/event/<model("event.event"):event>/qr'], type='http', auth='public')
    def event_qr(self, event, **post):
        if not event:
            return request.not_found()

        data = "%sevent/%s/register" % (request.httprequest.url_root, slug(event))

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        reader = StringIO()
        img_data = qr.make_image()
        img_data.save(reader, format="PNG")
        return http.send_file(reader, filename="event_%s.png" % (event.id), as_attachment=False)