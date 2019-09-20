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

# import psycopg2

_logger = logging.getLogger(__name__)

class HomePage(Controller):

    @http.route(['/API/load_banner'], methods=['GET', 'POST'], type='http', auth='public', csrf=False)
    def load_banner(self):

        master_banner_satu=request.env['slider.banner_satu'].search([])

        banner_satu=[]

        for banner in master_banner_satu:
            value_satu = OrderedDict()
            value_satu['image'] = '/web/image/slider.banner_satu/'+str(banner.id)+'/image' 
            banner_satu.append(value_satu)
        

        master_banner_dua=request.env['slider.banner_dua'].search([])

        banner_dua=[]

        for banner in master_banner_dua:
            value_dua = OrderedDict()
            value_dua['image'] = '/web/image/slider.banner_dua/'+str(banner.id)+'/image'
            banner_dua.append(value_dua)

        master_banner_tiga=request.env['slider.banner_tiga'].search([])

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