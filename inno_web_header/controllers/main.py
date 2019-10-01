import babel.dates
import itertools
import json
import pytz
import werkzeug

from collections import OrderedDict
from odoo import http, fields, _
from odoo.addons.website.controllers.main import QueryURL
from odoo.http import request
from odoo.tools import ustr



# class InnoHome(http.Controller):
#     @http.route('/', auth='public', website=True)
#     def index(self, debug=False):
#         return http.request.render('inno_web_header.home')

class InnoContactus(http.Controller):
    @http.route('/page/contact_us', auth='public', website=True)
    def index(self, debug=False):
        return http.request.render('inno_web_header.contact_us')

class InnoShop(http.Controller):
    @http.route('/page/shop', auth='public', website=True)
    def index(self, debug=False):
        return http.request.render('inno_web_header.shop')

class InnoEvents(http.Controller):
    @http.route('/page/events', auth='public', website=True)
    def index(self, debug=False):
        return http.request.render('inno_web_header.events')

class InnoBlog(http.Controller):
    @http.route('/page/blog', auth='public', website=True)
    def index(self, debug=False):
        return http.request.render('inno_web_header.blog')

class InnoPresentation(http.Controller):
    @http.route('/page/presentation', auth='public', website=True)
    def index(self, debug=False):
        return http.request.render('inno_web_header.presentation')