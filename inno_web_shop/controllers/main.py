# -*- coding: utf-8 -*-

import base64
import json
import werkzeug
import werkzeug.urls
import re

from odoo import http, SUPERUSER_ID
from odoo.http import request, Response

from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.website_sale.controllers import main

main.PPG = 24
PPG=main.PPG


class WebsiteSale(WebsiteSale):

    @http.route(['/shop/cart/update_option'], type='http', auth="public", website=True)
    def update_cart_popup(self):
        order = request.website.sale_get_order()
        return request.render("theme_stoneware.product_cart", {'website':request.website})
        
    @http.route(['/shop/cart/update_click/<product_id>'], type='http', auth="public", methods=['GET','POST'], website=True, csrf=False)
    def cart_update_click(self, product_id):
        sale_order = request.website.sale_get_order(force_create=True)
        if sale_order.state != 'draft':
            request.session['sale_order_id'] = None
            sale_order = request.website.sale_get_order(force_create=True)
        
        checking_data_product = sale_order.website_order_line.mapped("product_id")
        print("test checking data", checking_data_product)
        sale_order._cart_update(
            product_id=int(product_id),
            add_qty=int(1),
            set_qty=int(0)
        )

        domain=[
            ('id', '=', product_id)
        ]
        
        data_product=request.env['product.product'].search(domain)
        qty = sale_order.website_order_line.mapped("product_uom_qty")
        price = data_product.currency_id.symbol+' '+'{:,.0f}'.format(data_product.list_price)
        amount_total = data_product.currency_id.symbol+' '+'{:,.0f}'.format(sale_order.amount_total)
        product_id_qty = "1.0"
        name_product = re.sub('[^A-Za-z0-9]+', '', data_product.name)
        make_a_lower_char = name_product.lower()
        url_name = make_a_lower_char.replace(" ", "-")
        id_category = ""
        status = ""
        
        product_id = not isinstance(product_id, int) and int(product_id) or product_id
        
        if product_id in checking_data_product.ids:
            status = "update"
        else:
            status = "add"

        if data_product.public_categ_ids:
            id_category = data_product.public_categ_ids.ids[0]

        value = {
            "product_id" : data_product.product_tmpl_id.id,
            "product_id_awal" : product_id,
            "display_name" : data_product.with_context(display_default_code=False).display_name,
            "image_small" : "/web/image/product.product/"+str(product_id)+"/image_small",
            "qty" : product_id_qty,
            "jumlah_data_awal" : len(checking_data_product),
            "jumlah_qty" : sum(qty),
            "price" : price,
            "amount_total" : amount_total,
            "url_name" : url_name,
            "id_category" : id_category,
            "status" : status
        }
        return Response(json.dumps(value), content_type='application/json')
        
