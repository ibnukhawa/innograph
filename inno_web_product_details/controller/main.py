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
            dt_list = []
            for s in sales:
                picking_orders = picking.sudo().search([('sale_order_id','=',s.id),('state','=','done')])
                
                for order in picking_orders:
                    for qty_product in order.pack_operation_product_ids:
                        if qty_product.product_id.id == product.product_variant_id.id:
                            dt_list.append(qty_product.qty_done)
            if len(dt_list) > 0:
                qty = int(sum(dt_list))
            product.sudo().write({'counter_view': product.counter_view+1, 
                           'sold_product': qty})
        r = super(WebsiteSaleInherit, self).product(product, category, search, **kwargs)
        return r
