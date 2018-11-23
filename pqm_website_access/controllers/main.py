import re
from odoo import http
from odoo.http import request
from odoo.addons.website.controllers.main import Website


class Website(Website):
    @http.route('/', type='http', auth="public", website=True)
    def index(self, **kw):
        url = request.httprequest.url_root

        main_menu = request.env.ref('website.main_menu')
        homepage_menu = request.env['website.menu'].sudo().search([('parent_id', '=', main_menu.id)], order='sequence ASC')

        redirect_page = False
        for menu in homepage_menu:
            has_domain = re.search('^(?:https?:\/\/)?(?:[^@\/\n]+@)?(?:www\.)?([^:\/?\n]+)', menu.url, re.IGNORECASE)
            if menu.access_url == menu._url_type(url) and not has_domain:
                redirect_page = menu.url
                break

        if redirect_page:
            return request.redirect(redirect_page)
        else:
            return super(Website, self).index(**kw)
