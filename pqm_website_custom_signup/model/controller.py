# -*- coding: utf-8 -*-
from datetime import datetime

from odoo import http
from odoo.addons.auth_signup.controllers.main import AuthSignupHome
from odoo.addons.web.controllers.main import Home, ensure_db, set_cookie_and_redirect, login_and_redirect
from odoo.addons.website.controllers.main import Website
from odoo.http import request


class WebInherit(AuthSignupHome):
    @http.route()
    def web_auth_signup(self, *args, **kw):
        ensure_db()
        response = super(WebInherit, self).web_auth_signup(*args, **kw)
        response.qcontext.update({'redirect': '/page/homepage'})

        return response


class AuthSignupHome(Home):
    @http.route()
    def web_login(self, *args, **kw):
        ensure_db()
        response = super(AuthSignupHome, self).web_login(*args, **kw)
        response.qcontext.update({'redirect': '/page/homepage'})
        return response

class Website(Website):
    
    @http.route('/', type='http', auth="user", website=True)
    def index(self, **kw):
        page = 'homepage'
        main_menu = request.env.ref('website.main_menu', raise_if_not_found=False)
        if main_menu:
            first_menu = main_menu.child_id and main_menu.child_id[0]
            if first_menu:
                if first_menu.url and (not (first_menu.url.startswith(('/page/', '/?', '/#')) or (first_menu.url == '/'))):
                    return request.redirect(first_menu.url)
                if first_menu.url and first_menu.url.startswith('/page/'):
                    return request.env['ir.http'].reroute(first_menu.url)
        return self.page(page)

