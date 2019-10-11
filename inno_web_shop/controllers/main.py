# -*- coding: utf-8 -*-

import base64

import werkzeug
import werkzeug.urls

from odoo import http, SUPERUSER_ID
from odoo.http import request

from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.website_sale.controllers import main

main.PPG = 24
PPG=main.PPG


class WebsiteSale(WebsiteSale):

    @http.route(['/shop/cart/update_option'], type='http', auth="public", website=True)
    def update_cart_popup(self):
        order = request.website.sale_get_order()
        return request.render("theme_stoneware.product_cart", {'website':request.website})
        
