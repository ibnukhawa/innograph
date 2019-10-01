'''controllers'''
import json
import logging
from werkzeug.exceptions import Forbidden, NotFound

from odoo import http, tools, _
from odoo.http import request
from odoo.addons.base.ir.ir_qweb.fields import nl2br
from odoo.addons.website.models.website import slug
from odoo.addons.website.controllers.main import QueryURL
from odoo.addons.website_sale.controllers.main import WebsiteSale

_logger = logging.getLogger(__name__)

PPG = 20  # Products Per Page
PPR = 4   # Products Per Row

class WebsiteSale(WebsiteSale):
    
    @http.route(['/shop/quotation'], type='http', auth='public', website=True)
    def quotation(self, **post):
        order = request.website.sale_get_order()
        if order:
            from_currency = order.company_id.currency_id
            to_currency = order.pricelist_id.currency_id
            compute_currency = lambda price: from_currency.compute(price, to_currency)
            values = {
                'website_sale_order': order,
                'compute_currency': compute_currency
            }
            return request.render("inno_web_checkout.quotation", values)

    @http.route(['/shop/quotation_send'], type='http', auth='public', website=True)
    def quotation_send(self, **post):
        order = request.website.sale_get_order()
        if order:
            values = {
                'website_sale_order': order,
            }
            to_user = post.get('quote_to')
            email = post.get('email')
            if 'cc'in post:
                cc = post.get('cc')
            else:
                cc = ''
            company = post.get('company')
            phone = post.get('phone')
            if 'fax' in post:
                fax = post.get('fax')
            else:
                fax = ''
            if 'sales_name' in post:
                sales_name = post.get('sales_name')
            else:
                sales_name = ''
            sale_order = str(order.name) + '_draft'
            sale = str(order.name)
            url_link = str(request.httprequest.host_url) + 'my/orders/' + str(order.id)
            template_id = request.env.ref('inno_web_checkout.email_quotation_shop')
            if template_id:
                template_id.with_context(to_user=to_user, email=email, cc=cc, company=company,
                    phone=phone, fax=fax, sales_name=sales_name, sale_order=sale_order,
                    sale=sale, url_link=url_link).sudo().send_mail(order.id, force_send=True)
            return request.render("inno_web_checkout.quotation_send", values)
