# -*- coding: utf-8 -*-
from odoo import http, SUPERUSER_ID
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale

class WebsiteSaleInherit(WebsiteSale):

    def get_qty(self,destination, product):
        request._cr.execute(''' 
            select sum(product_uom_qty) as tot from stock_move where product_id='%d' and location_dest_id = '%d' and state='done';
            '''%(product,destination))
        return request._cr.dictfetchall()[0]

    @http.route(['/shop/product/<model("product.template"):product>'], type='http', auth="public", website=True)
    def product(self, product, category='', search='', **kwargs):
        qty = 0
        customer = request.env.ref('stock.stock_location_customers')
        if customer:
            result = self.get_qty(customer.id,product.product_variant_id.id)
            if result['tot'] != None:
                qty = result['tot']
        vals = {'counter_view': product.counter_view+1}
        if qty != 0:
            vals['sold_product'] = qty
        product.sudo().write(vals)
        viewer = product.get_view_product(product.counter_view+1)
        qty_sold = product.get_sold_qty(qty)
        r = super(WebsiteSaleInherit, self).product(product, category, search, **kwargs)
        r.qcontext['qty_viewer']=viewer.get('qty')
        r.qcontext['sat_viewer']=viewer.get('satuan')
        r.qcontext['qty_sold']=qty_sold.get('qty')
        r.qcontext['sat_sold']=qty_sold.get('satuan')
        return r
