# -*- coding: utf-8 -*-
from datetime import datetime
import unicodedata
import base64
from odoo import fields, http
from odoo.addons.website_event.controllers.main import WebsiteEventController
from odoo.addons.website.models.website import slug
from odoo.http import request
import werkzeug


class EventRegisterController(WebsiteEventController):

    @http.route(['/event/<model("event.event"):event>/registration/new'], type='http', auth="user", methods=['POST', 'GET'], website=True)
    def registration_new(self, event, **params):
        tickets = self._process_tickets_details(params)
        if not tickets:
            return request.redirect('/event/%s' % slug(event))
        user = request.env.user
        countries = request.env['res.country'].search([])
        return request.render("pqm_event_register.registration_new", {
            'countries': countries,
            'tickets': tickets, 
            'event': event, 
            'user': user, 
        })

    @http.route(['/event/<model("event.event"):event>/registration/confirm'], type='http', auth="user", methods=['POST'], website=True)
    def registration_confirm(self, event, **post):
        partner = request.env.user.partner_id
        partner_vals = self._process_partner_details(post)
        partner.write(partner_vals)
        if partner.parent_id:
            partner.parent_id.write(partner_vals)
        company_vals = self._process_company_details(post)
        if company_vals.values():
            if partner.parent_id:
                partner.parent_id.write(company_vals)
            else:
                company = request.env['res.partner'].sudo().create(company_vals)
                partner.parent_id = company.id

            finance = partner.parent_id.filtered(lambda r: r.is_event_finance == True)
            finance_vals = self._process_finance_details(post)
            if finance_vals.values():
                if finance:
                    finance[0].write(finance_vals)
                else:
                    finance = request.env['res.partner'].sudo().create(finance_vals)
                    finance.parent_id = partner.parent_id.id

        order = request.website.sale_get_order(force_create=True)
        order.order_line = False
        request.website.sale_reset()
        res = super(EventRegisterController, self).registration_confirm(event, **post)
        order = request.website.sale_get_order()
        if order:
            order_vals = self._process_order_details(post)
            event = event.sudo()
            if order_vals.values():
                order_vals['project_id'] = event.project_id.analytic_account_id.id
                order.write(order_vals)

        res.location = '/shop/confirm_order'
        return res

    def _process_company_details(self, details):
        company = {}
        for key, value in details.iteritems():
            if 'company_' in key and value:
                if isinstance(value, werkzeug.datastructures.FileStorage):
                    company[key.replace('company_', '')] = base64.b64encode(value.read())
                else:
                    company[key.replace('company_', '')] = value
        return company

    def _process_finance_details(self, details):
        finance = {
            'is_event_finance': True
        }
        for key, value in details.iteritems():
            if 'finance_' in key and value:
                if isinstance(value, werkzeug.datastructures.FileStorage):
                    finance[key.replace('finance_', '')] = base64.b64encode(value.read())
                else:
                    finance[key.replace('finance_', '')] = value
        return finance

    def _process_partner_details(self, details):
        partner = {
            'is_event_pic': True
        }
        for key, value in details.iteritems():
            if 'partner_' in key and value:
                if isinstance(value, werkzeug.datastructures.FileStorage):
                    partner[key.replace('partner_', '')] = base64.b64encode(value.read())
                else:
                    partner[key.replace('partner_', '')] = value
        return partner

    def _process_order_details(self, details):
        order = {}
        for key, value in details.iteritems():
            if 'order_' in key and value:
                if isinstance(value, werkzeug.datastructures.FileStorage):
                    order[key.replace('order_', '')] = base64.b64encode(value.read())
                else:
                    order[key.replace('order_', '')] = value
        return order

    def _process_registration_details(self, details):
        new_details = {}
        for key, value in details.iteritems():
            if '-' in key:
                new_details[key] = value
        return super(EventRegisterController, self)._process_registration_details(new_details)
