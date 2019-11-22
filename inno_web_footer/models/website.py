# -*- coding: utf-8 -*-

from odoo import models, fields
from odoo.http import request


class Website(models.Model):
    _inherit = 'website'

    social_instagram = fields.Char('Instagram Account')

    def getLogoFooter(self):
        url = request.httprequest.url_root
        url_new = url.replace("http://","")
        url_final = url_new[:-1]

        domain = [
            ('url', '=', url_final)
        ]
        menu_url = request.env['website.menu.url'].search(domain)
        images = '/web/image/website.menu.url/'+str(menu_url.id)+'/logo_footer/300x300'

        return images

