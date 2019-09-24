# -*- coding: utf-8 -*-
import json

import requests

import math

from odoo import http

from odoo.http import Controller, Response, request, route

from datetime import datetime, date, timedelta

from collections import OrderedDict
import logging
import re
import random

# import psycopg2

_logger = logging.getLogger(__name__)

class HomePage(Controller):

    # @http.route('/', type='http', auth="public", website=True)
    # def index(self, **kw):
    #     page = 'homepage'
    #     main_menu = request.website.menu_id or request.env.ref('website.main_menu', raise_if_not_found=False)
    #     if main_menu:
    #         first_menu = main_menu.child_id and main_menu.child_id[0]
    #         if first_menu:
    #             if first_menu.url and (not (first_menu.url.startswith(('/page/', '/?', '/#')) or (first_menu.url == '/'))):
    #                 return request.redirect(first_menu.url)
    #             if first_menu.url and first_menu.url.startswith('/page/'):
    #                 return request.env['ir.http'].reroute(first_menu.url)

    #     # return self.page(page)
    #     return http.request.render('website_pci_v2.home')    


    @http.route(['/API/load_banner'], methods=['GET', 'POST'], type='http', auth='public', csrf=False)
    def load_banner(self):

        master_banner_satu=request.env['slider.banner_satu'].search([],limit=5)

        banner_satu=[]

        for banner in master_banner_satu:
            value_satu = OrderedDict()
            value_satu['image'] = '/web/image/slider.banner_satu/'+str(banner.id)+'/image' 
            banner_satu.append(value_satu)
        

        master_banner_dua=request.env['slider.banner_dua'].search([],limit=5)

        banner_dua=[]

        for banner in master_banner_dua:
            value_dua = OrderedDict()
            value_dua['image'] = '/web/image/slider.banner_dua/'+str(banner.id)+'/image'
            banner_dua.append(value_dua)

        master_banner_tiga=request.env['slider.banner_tiga'].search([],limit=5)

        banner_tiga=[]

        for banner in master_banner_tiga:
            value_tiga = OrderedDict()
            value_tiga['image'] = '/web/image/slider.banner_tiga/'+str(banner.id)+'/image'
            banner_tiga.append(value_tiga)

        data = OrderedDict()
        data['banner_satu'] = banner_satu
        data['banner_dua'] = banner_dua
        data['banner_tiga'] = banner_tiga

        return Response(json.dumps(data), content_type='application/json')
    
    @http.route(['/API/load_category'], methods=['GET', 'POST'], type='http', auth='public', csrf=False)
    def load_category(self):
        domain=[
            ('show_in_website', '=', True)
        ]

        data_public_category =request.env['product.public.category'].search(domain,order="sequence ASC")
        data= []
        for category in data_public_category:
            name = category.name
            new_name = name.replace(" ", "-")
            image_url = '/web/image/product.public.category/'+str(category.id)+'/image/300x300'

            data.append({'name':category.name, 'background':category.background_color, 'image':image_url,'name_url':new_name+"-"+str(category.id) })


        return Response(json.dumps(data), content_type='application/json')

    
    @http.route(['/API/load_slider_tab'], methods=['GET', 'POST'], type='http', auth='public', csrf=False)
    def load_slider_tab(self):
        domain=[
            ('is_active', '=', True)
        ]

        data_slider_tabs =request.env['slider.tabs'].search(domain,order="sequence ASC")
        data= []
        for slider_tab in data_slider_tabs:
            
            data_slider = OrderedDict()
            data_product = []
        
            for product in slider_tab.product_ids:
                price =product.currency_id.symbol+' '+'{:,.2f}'.format(product.list_price)
                
                name_product = re.sub('[^A-Za-z0-9]+', '', product.name)
                a = name_product.lower()
                url_name = a.replace(" ", "-")
                
                image_product = '/web/image/product.template/'+str(product.id)+'/image/300x300'
                # print(str(product.list_price)+" "+name_product)
                data_product.append({'id':product.id, 'name':product.name,'url_name': url_name, 'image':image_product, 'price_label': price, 'price': product.list_price, 'currency':product.currency_id.symbol})
            
            data_slider['id_tab'] = slider_tab.id
            data_slider['name_tab'] = slider_tab.name
            data_slider['data_products'] = data_product

            data.append(data_slider)
        
        return Response(json.dumps(data), content_type='application/json')

    @http.route(['/API/multiple_category'], methods=['GET', 'POST'], type='http', auth='public', csrf=False)
    def multiple_category(self):
        domain=[
            ('is_active', '=', True)
        ]

        data_slider_multiple_category =request.env['slider.multiple_category'].search(domain)
        data= []

        for slider_multi in data_slider_multiple_category:
            
            data_slider = OrderedDict()
            # data_product = []
            title = ''
            # data_slider['category_ids'] = slider_multi.category_ids
            data_product = []
                
            for category in slider_multi.category_ids:
                if(title == ''):
                    title = category.name
                else:
                    title = title +", "+ category.name    
                # print("Test category" + str(title) + "id "+ str(category.id))
                domain=[
                    ('public_categ_ids', '=', category.id)
                ]
                master_product = request.env['product.template'].search(domain)
                
                for product in master_product:

                    # price =product.currency_id.symbol+' '+'{:,.2f}'.format(product.list_price)
                    price =product.currency_id.symbol+' '+'{:,.0f}'.format(product.list_price)
                    name_product = re.sub('[^A-Za-z0-9]+', '', product.name)
                    a = name_product.lower()
                    url_name = a.replace(" ", "-")
                    url_img='/web/image/product.template/'+str(product.id)+'/image/300x300'
                    data_product.append({'id':product.id, 'name':product.name,'url_name': url_name, 'image':url_img, 'price_label': price, 'price': product.list_price, 'currency':product.currency_id.symbol})

            data_slider['data_product']=data_product
            data_slider['title'] = title
            data.append(data_slider)
            
        
        return Response(json.dumps(data), content_type='application/json')