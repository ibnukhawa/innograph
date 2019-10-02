# -*- coding: utf-8 -*-
from odoo import http, SUPERUSER_ID
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale

class WebsiteSaleInherit(WebsiteSale):

    @http.route(['/shop/product/<model("product.template"):product>'], type='http', auth="public", website=True)
    def product(self, product, category='', search='', **kwargs):
        if product:
            qty = 0
            picking = request.env['stock.picking']
            sale_order = request.env['sale.order']
            sales = sale_order.sudo().search([ ('state','in',['sale','done'])])
            dt_product = product.product_variant_id.id
            for s in sales:
                picking_orders = s.order_line.sudo().search([('order_id','=',s.id),('product_id','=',dt_product)])
                for order in picking_orders:
                    qty += int(order.qty_delivered)
            product.sudo().write({'counter_view': product.counter_view+1, 
                           'sold_product': qty})
        r = super(WebsiteSaleInherit, self).product(product, category, search, **kwargs)
        return r
