# -*- coding:utf-8 -*-
""" X """
from odoo import http, SUPERUSER_ID
from odoo.http import request
from datetime import datetime, date
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
import werkzeug
import json
import pytz

class PQMEventCoupon(http.Controller):

    @http.route(['/coupon', '/coupon/page/<int:page>'], type='http', auth='public', website=True)
    def coupons(self, page=1, step=12, **kw):
        res = {}
        tz = pytz.timezone('Asia/Jakarta')

        # pqm core modification
        success = request.session.get('success', None)
        request.session['success'] = None
        message = request.session.get('message', None)
        request.session['message'] = None

        coupon_obj = request.env['event.coupon'].sudo()
        domain = [('state', 'in', ['available', 'draft'])]
        count = coupon_obj.search_count(domain)

        pager = request.website.pager(
            url = "/coupon",
            url_args = {
                'sortby': kw.get('sortby'),
            },
            total = count,
            page = page,
            step = step,
            scope = 5
        )

        sortby = 'name'
        if kw.get('sortby', 'name') == 'date':
            sortby = 'date_begin'
        
        coupons = coupon_obj.search(domain, limit=step, offset=pager['offset'])
        coupons = coupons.sorted(sortby)

        res = {
            'success': success,
            'message': message,
            'coupons': coupons,
            'sorted': sortby,
            'pager': pager,
        }
        return request.render("pqm_event_coupon.coupon_web_view", res)

class PQMEventCoupon(http.Controller):
    @http.route(['/shop/coupon/verify'], type='http', method=['GET'], auth='public', website=True)
    def verify_coupon(self, coupon_code=False, **kw):
        if not coupon_code:
            return json.dumps({
                'success': False,
                'message': 'No Coupoon Code'
            })
        order = request.website.sale_get_order()
        if order:
            order = order.sudo()
            # check if order has coupon applied, 1 order 1 coupon
            if order.coupon_id:
                return json.dumps({'success': False, 'message': 'Can not apply more than 1 Coupon'})
            # get qty order
            qty_order = sum(order.order_line.mapped('product_uom_qty'))
            # search coupon
            coupon_domain = [('code', '=', coupon_code), ('state', '=', 'available')]
            coupon = request.env['event.coupon'].search(coupon_domain, limit=1)
            if qty_order < coupon.minimum_order:
                # if minimum order not valid
                return json.dumps({'success': False, 'message': 'Minimum Quantity for this coupon is %s' % coupon.minimum_order})
            elif coupon:
                coupon = coupon.sudo()
                # Apply discount to Order Line
                coupon_usage = request.env['event.coupon.usage']
                for line in order.order_line:
                    if line.event_id.id in coupon.event_ids._ids:
                        if coupon.apply_method == 'percent':
                            line.write({'discount': coupon.discount_percentage})
                        else:
                            line.discount = 50
                        # Update Usage coupon
                        usage = coupon_usage.sudo().create({'event_id': line.event_id.id,
                                                            'order_id': line.order_id.id,
                                                            'coupon_id': coupon.id})
                        if usage:
                            coupon.write({'coupon_usage_ids': [(4, usage.id)]})

                            # Update Coupon for SO
                            order.coupon_id = coupon.id
                        else:
                            return json.dumps(
                                {'success': False, 'message': 'Coupon not applicable'})
            else:
                # If coupon not available
                return json.dumps({'success': False, 'message': 'Coupon code not Available'})
        return json.dumps({'success': True, 'message': 'Coupon code applied'})

    @http.route(['/shop/coupon/remove'], type='http', method=['GET'], auth='public', website=True)
    def remove_coupon(self, **kw):
        order = request.website.sale_get_order()
        if order:
            order = order.sudo()
            coupon_id = order.coupon_id.id
            order.coupon_id = False
            for line in order.order_line:
                # Set discount to 0
                line.discount = 0
                # remove usage on Coupon
                event_id = line.event_id.id
                coupon_usage = request.env['event.coupon.usage']
                usage = coupon_usage.search([('coupon_id', '=', coupon_id),
                                             ('order_id', '=', order.id),
                                             ('event_id', '=', event_id)])
                if usage:
                    usage.unlink()

        return json.dumps({'success': True})

    @http.route(['/shop/order/cancel'], type='http', method=['GET'], auth='public', website=True)
    def order_cancel(self, **kw):
        order = request.website.sale_get_order()
        if order:
            self.remove_coupon(**kw)
            order.order_line = False
            request.website.sale_reset()
        return request.redirect('/event')

