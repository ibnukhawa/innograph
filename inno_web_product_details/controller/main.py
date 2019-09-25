# -*- coding: utf-8 -*-
from odoo import http, SUPERUSER_ID
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale

class WebsiteSaleInherit(WebsiteSale):

    @http.route(['/shop/product/<model("product.template"):product>'], type='http', auth="public", website=True)
    def product(self, product, category='', search='', **kwargs):
        if product:
            qty = 0
            order_line = request.env['sale.order.line']
            sale_order = request.env['sale.order']
            sales = sale_order.sudo().search([ ('state','in',('sale','done'))])
            for s in sales:
                orders = order_line.sudo().search([('order_id','=',s.id),('product_id','=',product.id)])
                for order in orders:
                        qty += order.product_uom_qty
            product.sudo().write({'counter_view': product.counter_view+1, 
                           'sold_product': qty})
        r = super(WebsiteSaleInherit, self).product(product, category, search, **kwargs)
        return r
