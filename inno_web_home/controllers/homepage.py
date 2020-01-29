# -*- coding: utf-8 -*-
import json

import requests

import math

from odoo import http

from odoo.http import Controller, Response, request, route

from datetime import datetime, date, timedelta

from odoo.addons.website.models.website import slug

from collections import OrderedDict
import logging
import re
import random


from odoo.tools.translate import _
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.web.controllers.main import Home
from odoo.addons.website_sale.controllers.main import TableCompute
from odoo.addons.website_sale.controllers.main import QueryURL
from odoo.addons.website_sale.controllers import main
from werkzeug.exceptions import Forbidden, NotFound

main.PPG = 18
PPG=main.PPG
PPR = 4   # Products Per Row


# import psycopg2

_logger = logging.getLogger(__name__)

class HomePage(Controller):

    @http.route(['/API/load_banner/<url>'], methods=['GET', 'POST'], type='http', auth='public', csrf=False)
    def load_banner(self,url):
        
        domain_menu=[
            ('url', '=', url)
        ]
        menu_url=request.env['website.menu.url'].search(domain_menu)
        
        domain=[
            ('access_url', '=', menu_url.id)
        ]
        master_banner_satu=request.env['slider.banner_satu'].search(domain,limit=5)

        banner_satu=[]

        for banner in master_banner_satu:
            value_satu = OrderedDict()
            value_satu['url']   = banner.url
            value_satu['image'] = '/web/image/slider.banner_satu/'+str(banner.id)+'/image' 
            banner_satu.append(value_satu)
        

        master_banner_dua=request.env['slider.banner_dua'].search(domain,limit=5)

        banner_dua=[]

        for banner in master_banner_dua:
            value_dua = OrderedDict()
            value_dua['url']    = banner.url
            value_dua['image']  = '/web/image/slider.banner_dua/'+str(banner.id)+'/image'
            banner_dua.append(value_dua)

        master_banner_tiga=request.env['slider.banner_tiga'].search(domain,limit=5)

        banner_tiga=[]

        for banner in master_banner_tiga:
            value_tiga = OrderedDict()
            value_tiga['url']   = banner.url
            value_tiga['image'] = '/web/image/slider.banner_tiga/'+str(banner.id)+'/image'
            banner_tiga.append(value_tiga)

        data = OrderedDict()
        data['banner_satu'] = banner_satu
        data['banner_dua'] = banner_dua
        data['banner_tiga'] = banner_tiga

        return Response(json.dumps(data), content_type='application/json')
    
    @http.route(['/API/load_category/<url>'], methods=['GET', 'POST'], type='http', auth='public', csrf=False)
    def load_category(self,url):
        domain_menu=[
            ('url', '=', url)
        ]
        menu_url=request.env['website.menu.url'].search(domain_menu)
        
        domain=[
            ('show_in_website', '=', True),
            ('access_url','=', menu_url.id)
        ]

        data_public_category =request.env['product.public.category'].search(domain,order="sequence ASC")
        data= []
        for category in data_public_category:
            name = category.name
            new_name = name.replace(" ", "-")
            image_url = '/web/image/product.public.category/'+str(category.id)+'/image/300x300'

            data.append({'name':category.name, 'background':category.background_color, 'image':image_url,'name_url':new_name+"-"+str(category.id) })


        return Response(json.dumps(data), content_type='application/json')

    
    @http.route(['/API/load_slider_tab/<url>'], methods=['GET', 'POST'], type='http', auth='public', csrf=False)
    def load_slider_tab(self, url):
        
        domain_menu=[
            ('url', '=', url)
        ]
        menu_url=request.env['website.menu.url'].search(domain_menu)
        
        domain=[
            ('is_active', '=', True),
            ('access_url', '=', menu_url.id)
        ]

        data_slider_tabs =request.env['slider.tabs'].search(domain,order="sequence ASC")
        data= []
        for slider_tab in data_slider_tabs:
            
            data_slider = OrderedDict()
            data_product = []
        
            for product in slider_tab.product_ids:
                price =product.currency_id.symbol+' '+'{:,.2f}'.format(product.website_price)
                
                name_product = re.sub('[^A-Za-z0-9]+', '', product.name)
                a = name_product.lower()
                url_name = a.replace(" ", "-")

                id_category = ""

                if(product.public_categ_ids):
                    id_category = product.public_categ_ids.ids[0]
                
                
                image_product = '/web/image/product.template/'+str(product.id)+'/image/300x300'
                data_product.append({'id':product.id, 'name':product.name,'url_name': url_name, 'image':image_product, 'price_label': price, 'price': product.website_price, 'currency':product.currency_id.symbol,'id_category':id_category})
            
            data_slider['id_tab'] = slider_tab.id
            data_slider['name_tab'] = slider_tab.name
            data_slider['data_products'] = data_product

            data.append(data_slider)
        
        return Response(json.dumps(data), content_type='application/json')

    @http.route(['/API/multiple_category/<url>'], methods=['GET', 'POST'], type='http', auth='public', csrf=False)
    def multiple_category(self,url):
        domain_menu=[
            ('url', '=', url)
        ]

        menu_url=request.env['website.menu.url'].search(domain_menu)
        
        domain=[
            ('is_active', '=', True),
            ('access_url', '=', menu_url.id)
        ]

        data_slider_multiple_category =request.env['slider.multiple_category'].search(domain,limit=4)
        data= []

        for slider_multi in data_slider_multiple_category:
            
            data_slider = OrderedDict()
            title = ''
            data_product = []
                
            for category in slider_multi.category_ids:
                if(title == ''):
                    title = category.name
                else:
                    title = title +", "+ category.name    
                domain=[
                    ('public_categ_ids', '=', category.id)
                ]
                master_product = request.env['product.template'].search(domain,limit=6)
                
                for product in master_product:

                    price =product.currency_id.symbol+' '+'{:,.0f}'.format(product.website_price)
                    name_product = re.sub('[^A-Za-z0-9]+', '', product.name)
                    a = name_product.lower()
                    url_name = a.replace(" ", "-")
                    url_img='/web/image/product.template/'+str(product.id)+'/image/300x300'
                    data_product.append({'id':product.id, 'name':product.name,'url_name': url_name, 'image':url_img, 'price_label': price, 'price': product.website_price, 'currency':product.currency_id.symbol,'id_category':product.public_categ_ids.ids[0]})

            data_slider['data_product']=data_product
            data_slider['title'] = title
            data.append(data_slider)
            
        
        return Response(json.dumps(data), content_type='application/json')

    @http.route(['/API/load_for_you'], methods=['GET', 'POST'], type='http', auth='public', csrf=False)
    def for_you(self):

        user_id = request.uid
        
        data_res_users = request.env['res.users'].search([('id', '=', user_id)])
        data_slider= OrderedDict()
        data= []
        data_product = []
        if data_res_users.login != False :
            limit = 18
            for index, product in enumerate(data_res_users.product_ids):
                
                price =product.currency_id.symbol+' '+'{:,.2f}'.format(product.website_price)
                
                name_product = re.sub('[^A-Za-z0-9]+', '', product.name)
                a = name_product.lower()
                url_name = a.replace(" ", "-")


                id_category = ""

                if(product.public_categ_ids):
                    id_category = product.public_categ_ids.ids[0]
                
                image_product = '/web/image/product.template/'+str(product.id)+'/image/300x300'
                data_product.append({'id':product.id, 'name':product.name,'url_name': url_name, 'image':image_product, 'price_label': price, 'price': product.website_price, 'currency':product.currency_id.symbol, 'id_category':id_category})

                if index == limit:
                    break

            data_slider['status'] = True
            data_slider['message'] = "Lanjutkan Brow !!"
            data_slider['data_products'] = data_product

        else:

            data_slider['status'] = False
            data_slider['message'] = "User id tidak di temukan"
            data_slider['data_products'] = data_product

        data.append(data_slider)
        
        
        return Response(json.dumps(data), content_type='application/json')

    @http.route(['/shop/tabs/<id>','/shop/tabs/<id>/page/<int:page>'], type='http', auth="public", website=True)
    def tabs_list(self, page=0, id='', category=None, search='', ppg=False, **post):
        user_id = request.uid
        if ppg:
            try:
                ppg = int(ppg)
            except ValueError:
                ppg = PPG
            post["ppg"] = ppg
        else:
            ppg = PPG

        if category:
            category = request.env['product.public.category'].search([('id', '=', int(category))], limit=1)
            if not category:
                raise NotFound()

        attrib_list = request.httprequest.args.getlist('attrib')
        attrib_values = [map(int, v.split("-")) for v in attrib_list if v]
        attributes_ids = set([v[0] for v in attrib_values])
        attrib_set = set([v[1] for v in attrib_values])
        
        if id == 'for_you':
            filter_product = request.env['res.users'].search([('id', '=', user_id)])
        else:   
            filter_product = request.env['slider.tabs'].search([('id', '=', id)])
        id_products = []

        for value in filter_product.product_ids:
            id_products.append(value.id)
        
        domain = [('id', 'in', id_products)]

        keep = QueryURL('/shop', category=category and int(category), search=search, attrib=attrib_list, order=post.get('order'))
        pricelist_context = dict(request.env.context)
        if not pricelist_context.get('pricelist'):
            pricelist = request.website.get_current_pricelist()
            pricelist_context['pricelist'] = pricelist.id
        else:
            pricelist = request.env['product.pricelist'].browse(pricelist_context['pricelist'])

        request.context = dict(request.context, pricelist=pricelist.id, partner=request.env.user.partner_id)

        url = "/shop/tabs/"+id
        if search:
            post["search"] = search
        if attrib_list:
            post['attrib'] = attrib_list

        categs = request.env['product.public.category'].search([('parent_id', '=', False)])
        Product = request.env['product.template']

        parent_category_ids = []
        if category:
            url = "/shop/category/%s" % slug(category)
            parent_category_ids = [category.id]
            current_category = category
            while current_category.parent_id:
                parent_category_ids.append(current_category.parent_id.id)
                current_category = current_category.parent_id

        product_count = Product.search_count(domain)
        pager = request.website.pager(url=url, total=product_count, page=page, step=ppg, scope=7, url_args=post)
        products = Product.search(domain, limit=ppg, offset=pager['offset'])

        ProductAttribute = request.env['product.attribute']
        if products:
            selected_products = Product.search(domain, limit=False)
            attributes = ProductAttribute.search([('attribute_line_ids.product_tmpl_id', 'in', selected_products.ids)])
        else:
            attributes = ProductAttribute.browse(attributes_ids)

        from_currency = request.env.user.company_id.currency_id
        to_currency = pricelist.currency_id
        compute_currency = lambda price: from_currency.compute(price, to_currency)


        values = {
            'search': search,
            'category': category,
            'attrib_values': attrib_values,
            'attrib_set': attrib_set,
            'pager': pager,
            'pricelist': pricelist,
            'products': products,
            'search_count': product_count,  # common for all searchbox
            'bins': TableCompute().process(products, ppg),
            'rows': PPR,
            'categories': categs,
            'attributes': attributes,
            'compute_currency': compute_currency,
            'keep': keep,
            'parent_category_ids': parent_category_ids,
        }
        if category:
            values['main_object'] = category
        return request.render("website_sale.products", values)

    

class WebsiteSale(WebsiteSale):
    @http.route(['/shop/product/<model("product.template"):product>'], type='http', auth="public", website=True)
    def product(self, product, category='', search='', **kwargs):
        r = super(WebsiteSale, self).product(product, category, search, **kwargs)
        user_id = request.uid
        data_user = request.env['res.users'].search([('id', '=', user_id)])
        
        data_product = []
        for prod in data_user.product_ids:
            data_product.append(prod.id)

        if (product.id not in data_product):
            data_product.insert(0,product.id)

        data_user.write({'product_ids': [(6, 0, data_product)]})
        return r

class AuthSignupHome(Home):
    @http.route('/web/signup', type='http', auth='public', website=True)
    def web_auth_signup(self, *args, **kw):
        qcontext = self.get_auth_signup_qcontext()
        
        url = request.httprequest.url_root
        url_new = url.replace("http://","")
        url_final =  url_new[:-1]

        domain_menu=[
            ('url', '=', url_final)
        ]
        menu_url=request.env['website.menu.url'].search(domain_menu)

        qcontext['image']='/web/image/website.menu.url/'+str(menu_url.id)+'/logo_footer/200x130'
        if not qcontext.get('token') and not qcontext.get('signup_enabled'):
            raise werkzeug.exceptions.NotFound()

        if 'error' not in qcontext and request.httprequest.method == 'POST':
            try:
                self.do_signup(qcontext)
                return super(AuthSignupHome, self).web_login(*args, **kw)
            except (SignupError, AssertionError), e:
                if request.env["res.users"].sudo().search([("login", "=", qcontext.get("login"))]):
                    qcontext["error"] = _("Another user is already registered using this email address.")
                else:
                    _logger.error(e.message)
                    qcontext['error'] = _("Could not create a new account.")

        return request.render('auth_signup.signup', qcontext)
