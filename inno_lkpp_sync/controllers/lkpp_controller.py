# -*- coding: utf-8 -*-
import json

import requests

import math

from odoo.http import Controller, Response, request, route

from datetime import datetime, date, timedelta

from collections import OrderedDict

API = 'https://e-katalog.lkpp.go.id/api/'
URL = 'http://demo.innograph.com'


class LKPPController(Controller):
    """ Controller for JSON, switch the type between 'http' and 'json' if trouble happens. """
  
    # @route('/lkpp/all_produk', methods=['GET', 'POST'], type='http', auth='none')
    # def lkpp_all_product(self, **kwargs):
    #     # URL Parameters
    #     key = kwargs.get('secretkey')
    #     # per_page = kwargs.get('per_page', 500)
    #     # page = kwargs.get('page', 1)
    #     # order_by = kwargs.get('order_by', 'create_date')
    #     # sort = kwargs.get('sort', 'desc')

    #     request.env['ir.config_parameter'].sudo().get_param('lkpp.secretkey', default='')

    #     data = {'key': key}

    #     return Response(json.dumps(data), content_type='application/json')


    # @route('/lkpp/updated_produk', methods=['GET', 'POST'], type='http', auth='none')
    # def lkpp_updated_product(self, **kwargs):
    #     # URL Parameters
    #     key = kwargs.get('secretkey')
    #     # per_page = kwargs.get('per_page', 500)
    #     # page = kwargs.get('page', 1)
    #     # start_date = kwargs.get('start_date')
    #     # end_date = kwargs.get('end_date')
    #     # order_by = kwargs.get('order_by', 'create_date')
    #     # sort = kwargs.get('sort', 'desc')

    #     request.env['ir.config_parameter'].sudo().get_param('lkpp.secretkey', default='')

    #     data = {'key': key}

    #     return Response(json.dumps(data), content_type='application/json')


    # @route('/lkpp/produk', methods=['GET', 'POST'], type='http', auth='none')
    # def lkpp_product(self, **kwargs):
    #     # URL Parameters
    #     key = kwargs.get('secretkey')
    #     # no_produk_penyedia = kwargs.get('no_produk_penyedia')

    #     # if not no_produk_penyedia:
    #     #     return Response('No. produk penyedia tidak valid!', status=400)

    #     request.env['ir.config_parameter'].sudo().get_param('lkpp.secretkey', default='')

    #     data = {'key': key}

    #     return Response(json.dumps(data), content_type='application/json')

    @route('/lkpp/all_produk', methods=['GET', 'POST'], type='http', auth='none', csrf=False)
    def lkpp_all_product(self, **kwargs):
        # URL Parameters
        key = kwargs.get('secretkey')
        per_page_url = kwargs.get('per_page', '500')
        per_page = int(per_page_url)
        page_url = kwargs.get('page', '0')
        page = int(page_url)
        order_by = kwargs.get('order_by', 'create_date')
        sort = kwargs.get('sort', 'desc')

        orderby=order_by+" "+sort
        
        data_all = []
        data_config=request.env['ir.config_parameter'].sudo().get_param('lkpp.secretkey', default='')
        id_penawaran_lkpp=request.env['ir.config_parameter'].sudo().get_param('lkpp.penawaran_id', default=None)
        domain=[
            ('active', '=', True),
            ('active_product', '=', True),
            ('unspsc', '!=', False),
            ('lkpp_category_id', '!=', False),
            ('lkpp_manufacturer_id', '!=', False),
            ('lkpp_uom_id', '!=', False),
            ('valid_date', '!=', False)
        ]
        if data_config == key:
            records = request.env['product.template'].sudo().search(domain,offset=page, limit=per_page,order=orderby)
            total = records.search_count(domain)

            total_page = math.ceil(total/per_page)
            for record in records:


                data_product = OrderedDict()
                url_produk=URL+'/shop/product/'+str(record.id)
                url_50=URL+'/web/image/product.template/'+str(record.id)+'/image/50x50'
                url_100=URL+'/web/image/product.template/'+str(record.id)+'/image/100x100'
                url_300=URL+'/web/image/product.template/'+str(record.id)+'/image/300x300'
                url_800=URL+'/web/image/product.template/'+str(record.id)+'/image/800x800'

                product_informasi = OrderedDict()
                
                product_informasi['unspsc'] = record.unspsc
                product_informasi['id_penawaran_lkpp'] = id_penawaran_lkpp
                product_informasi['id_kategori_produk_lkpp'] = record.lkpp_category_id
                product_informasi['nama_produk'] = record.name
                product_informasi['no_produk_penyedia'] = record.default_code
                product_informasi['id_manufaktur'] = record.lkpp_manufacturer_id
                product_informasi['id_unit_pengukuran_lkpp'] = record.lkpp_uom_id

                if record.deskripsi_singkat == False:
                    deskripsi_singkat = None
                else:
                    deskripsi_singkat = record.deskripsi_singkat

                product_informasi['deskripsi_singkat'] = deskripsi_singkat

                if record.deskripsi_lengkap == False:
                    deskripsi_lengkap = None
                else:
                    deskripsi_lengkap = record.deskripsi_lengkap

                product_informasi['deskripsi_lengkap'] = deskripsi_lengkap
                product_informasi['kuantitas_stok'] = record.qty_available
                product_informasi['tanggal_update'] = record.write_date

                if record.active_product == True:
                    active_product = 1
                else:
                    active_product = 0
                
                product_informasi['produk_aktif'] = active_product


                if record.local_product == False:
                    local_product = 0
                else:
                    local_product = 1

                product_informasi['apakah_produk_lokal'] = local_product
                product_informasi['berlaku_sampai'] = record.valid_date
                product_informasi['url_produk'] = url_produk
                product_informasi['image_50x50'] = url_50
                product_informasi['image_100x100'] = url_100
                product_informasi['image_300x300'] = url_300
                product_informasi['image_800x800'] = url_800


                data_attr_all = []
                product_variants=request.env['product.attribute'].search([('attribute_line_ids.product_tmpl_id', '=', record.id)])

                for attr in product_variants:

                    attribute = OrderedDict()
                    deskripsi = ""
                    for value in attr.value_ids:
                        deskripsi = deskripsi +" "+value.name
                    
                    attribute['label'] = attr.name
                    attribute['deskripsi'] = deskripsi
                    data_attr_all.append(attribute)

                product_spesifikasi=({
                    'item':data_attr_all,
                    'tanggal_update':record.write_date
                })

                image = OrderedDict()
                image['deskripsi']=deskripsi_singkat
                image['image_50x50']=url_50
                image['image_100x100']=url_100
                image['image_300x300']=url_300
                image['image_800x800']=url_800

                data_image=({
                    'item':image,
                    'tanggal_update':record.write_date
                })

                data_harga = OrderedDict()
                data_harga['harga_retail'] = record.website_price
                data_harga['harga_pemerintah'] = record.lkpp_govt_price
                data_harga['ongkos_kirim'] = 0
                data_harga['kurs_id'] = 1
                data_harga['tanggal_update'] = record.write_date

                # input data to data_product

                data_product['informasi']=product_informasi
                data_product['spesifikasi'] = product_spesifikasi
                data_product['image'] = data_image
                data_product['harga'] = data_harga
                data_product['lampiran'] = None
                data_all.append(data_product)
            
            data = OrderedDict()
            data['total'] = total
            data['current_page'] = page
            data['per_page'] = per_page
            data['total_page'] = total_page
            data['produk'] = data_all
            
        else:
            data = {'error': data_config
            }
        
        return Response(json.dumps(data), content_type='application/json')


    @route('/lkpp/updated_produk', methods=['GET', 'POST'], type='http', auth='none')
    def lkpp_updated_product(self, **kwargs):
        # URL Parameters
        key = kwargs.get('secretkey')
        per_page_url = kwargs.get('per_page', '500')
        per_page = int(per_page_url)
        page_url = kwargs.get('page', '1')
        page = int(page_url)
        start_date = kwargs.get('start_date',False)
        end_date = kwargs.get('end_date',False)
        order_by = kwargs.get('order_by', 'write_date')
        sort = kwargs.get('sort', 'desc')
        today = date.today()

        start=str(today)+" 00:00:00"
        end = str(today)+" 23:59:59"
        start_obj =datetime.strptime(start, '%Y-%m-%d %H:%M:%S') - timedelta(hours=7)
        end_obj =datetime.strptime(end, '%Y-%m-%d %H:%M:%S') - timedelta(hours=7)

        if start_date == False:
            start_date = start_obj
            end_date = end_obj

        orderby=order_by+" "+sort
        
        data_all = []
        data_config=request.env['ir.config_parameter'].sudo().get_param('lkpp.secretkey', default='')
        id_penawaran_lkpp=request.env['ir.config_parameter'].sudo().get_param('lkpp.penawaran_id', default=None)
        
        if data_config == key:
            
            # records = request.env['product.template'].sudo().search(domain,offset=page, limit=per_page,order=orderby)
            
            query="SELECT * from product_template where to_char(write_date, 'yyyy-mm-dd HH24:MI:SS') BETWEEN '"+str(start_date)+"' and '"+str(end_date)+"' and active != False and active_product != False order by "+orderby+" OFFSET "+str((page-1)*per_page)+" LIMIT "+str(per_page)
            
            records = request.env.cr.execute(query)

            
            res = request.env.cr.dictfetchall()
            total = len(res)

            total_page = math.ceil(total/per_page)
            for record in res:

                data_product = OrderedDict()
                result=request.env['product.template'].sudo().search([('id', '=', record['id'])])
                
                url_produk=URL+'/shop/product/'+str(record['id'])
                url_50=URL+'/web/image/product.template/'+str(record['id'])+'/image/50x50'
                url_100=URL+'/web/image/product.template/'+str(record['id'])+'/image/100x100'
                url_300=URL+'/web/image/product.template/'+str(record['id'])+'/image/300x300'
                url_800=URL+'/web/image/product.template/'+str(record['id'])+'/image/800x800'
                
                product_informasi = OrderedDict()

                product_informasi['unspsc'] = record['unspsc']
                product_informasi['id_penawaran_lkpp'] = id_penawaran_lkpp
                product_informasi['id_kategori_produk_lkpp'] = record['lkpp_category_id']
                product_informasi['nama_produk'] = record['name']
                product_informasi['no_produk_penyedia'] = record['default_code']
                product_informasi['id_manufaktur'] = record['lkpp_manufacturer_id']
                product_informasi['id_unit_pengukuran_lkpp'] = result.lkpp_uom_id


                if result.deskripsi_singkat == False:
                    deskripsi_singkat = None
                else:
                    deskripsi_singkat = result.deskripsi_singkat

                product_informasi['deskripsi_singkat'] = deskripsi_singkat

                if result.deskripsi_lengkap == False:
                    deskripsi_lengkap = None
                else:
                    deskripsi_lengkap = result.deskripsi_lengkap
                
                product_informasi['deskripsi_lengkap'] = deskripsi_lengkap
                product_informasi['kuantitas_stok'] = result.qty_available
                product_informasi['tanggal_update'] = record['write_date']

                if record['active_product'] == True:
                    active_product = 1
                else:
                    active_product = 0
                
                product_informasi['produk_aktif'] = active_product

                if record['local_product'] == False:
                    local_product = 0
                else:
                    local_product = 1

                product_informasi['apakah_produk_lokal'] = local_product
                product_informasi['berlaku_sampai'] = record['valid_date']
                product_informasi['url_produk'] = url_produk
                product_informasi['image_50x50'] = url_50
                product_informasi['image_100x100'] = url_100
                product_informasi['image_300x300'] = url_300
                product_informasi['image_800x800'] = url_800

                data_attr_all = []
                product_variants=request.env['product.attribute'].search([('attribute_line_ids.product_tmpl_id', '=', record['id'])])

                for attr in product_variants:
                    attribute = OrderedDict()
                    deskripsi = ""
                    for value in attr.value_ids:
                        deskripsi = deskripsi +" "+value.name
                    
                    attribute['label'] = attr.name
                    attribute['deskripsi'] = deskripsi
                    data_attr_all.append(attribute)
                    

                product_spesifikasi=({
                    'item':data_attr_all,
                    'tanggal_update':result.write_date
                })

                image = OrderedDict()
                image['deskripsi']=deskripsi_singkat
                image['image_50x50']=url_50
                image['image_100x100']=url_100
                image['image_300x300']=url_300
                image['image_800x800']=url_800

                data_image=({
                    'item':image,
                    'tanggal_update':result.write_date
                })

                data_harga = OrderedDict()
                data_harga['harga_retail'] = result.website_price
                data_harga['harga_pemerintah'] = result.lkpp_govt_price
                data_harga['ongkos_kirim'] = 0
                data_harga['kurs_id'] = 1
                data_harga['tanggal_update'] = result.write_date

                data_product['informasi'] = product_informasi
                data_product['spesifikasi'] = product_spesifikasi
                data_product['image'] = data_image
                data_product['harga'] = data_harga
                data_product['lampiran'] = None
                data_all.append(data_product)
            
            data = OrderedDict()
            data['total'] = total
            data['current_page'] = page
            data['per_page'] = per_page
            data['total_page'] = total_page
            data['produk'] = data_all
        else:
            data = {'error': data_config
            }
        
        return Response(json.dumps(data), content_type='application/json')


    @route('/lkpp/produk', methods=['GET', 'POST'], type='http', auth='none')
    def lkpp_product(self, **kwargs):
        # URL Parameters
        key = kwargs.get('secretkey')
        no_produk_penyedia = kwargs.get('no_produk_penyedia')

        if not no_produk_penyedia:
            return Response('No. produk penyedia tidak valid!', status=400)

        data_product = OrderedDict()
        data_config=request.env['ir.config_parameter'].sudo().get_param('lkpp.secretkey', default='')
        id_penawaran_lkpp=request.env['ir.config_parameter'].sudo().get_param('lkpp.penawaran_id', default=None)
        domain=[
            ('default_code','=',no_produk_penyedia),
            ('active', '=', True),
            ('active_product', '=', True)
        ]
        if data_config == key:
            records = request.env['product.template'].sudo().search(domain)
            
            for record in records:

                url_produk=URL+'/shop/product/'+str(record.id)
                url_50=URL+'/web/image/product.template/'+str(record.id)+'/image/50x50'
                url_100=URL+'/web/image/product.template/'+str(record.id)+'/image/100x100'
                url_300=URL+'/web/image/product.template/'+str(record.id)+'/image/300x300'
                url_800=URL+'/web/image/product.template/'+str(record.id)+'/image/800x800'

                product_informasi = OrderedDict()

                product_informasi['unspsc'] = record.unspsc
                product_informasi['id_penawaran_lkpp'] = id_penawaran_lkpp
                product_informasi['id_kategori_produk_lkpp'] = record.lkpp_category_id
                product_informasi['nama_produk'] = record.name
                product_informasi['no_produk_penyedia'] = record.default_code
                product_informasi['id_manufaktur'] = record.lkpp_manufacturer_id
                product_informasi['id_unit_pengukuran_lkpp'] = record.lkpp_uom_id

                if record.deskripsi_singkat == False:
                    deskripsi_singkat = None
                else:
                    deskripsi_singkat = record.deskripsi_singkat

                product_informasi['deskripsi_singkat'] = deskripsi_singkat

                if record.deskripsi_lengkap == False:
                    deskripsi_lengkap = None
                else:
                    deskripsi_lengkap = record.deskripsi_lengkap

                product_informasi['deskripsi_lengkap'] = deskripsi_lengkap
                product_informasi['kuantitas_stok'] = record.qty_available
                product_informasi['tanggal_update'] = record.write_date

                if record.active_product == True:
                    active_product = 1
                else:
                    active_product = 0
                
                product_informasi['produk_aktif'] = active_product


                if record.local_product == False:
                    local_product = 0
                else:
                    local_product = 1

                product_informasi['apakah_produk_lokal'] = local_product
                product_informasi['berlaku_sampai'] = record.valid_date
                product_informasi['url_produk'] = url_produk
                product_informasi['image_50x50'] = url_50
                product_informasi['image_100x100'] = url_100
                product_informasi['image_300x300'] = url_300
                product_informasi['image_800x800'] = url_800


                
                data_attr_all = []
                product_variants=request.env['product.attribute'].search([('attribute_line_ids.product_tmpl_id', '=', record.id)])

                for attr in product_variants:
                    attribute = OrderedDict()
                    deskripsi = ""
                    for value in attr.value_ids:
                        deskripsi = deskripsi +" "+value.name
                    
                    attribute['label'] = attr.name
                    attribute['deskripsi'] = deskripsi
                    data_attr_all.append(attribute)

                product_spesifikasi=({
                    'item':data_attr_all,
                    'tanggal_update':record.write_date
                })

                image = OrderedDict()
                image['deskripsi']=deskripsi_singkat
                image['image_50x50']=url_50
                image['image_100x100']=url_100
                image['image_300x300']=url_300
                image['image_800x800']=url_800

                data_image=({
                    'item':image,
                    'tanggal_update':record.write_date
                })

                data_harga = OrderedDict()
                data_harga['harga_retail'] = record.website_price
                data_harga['harga_pemerintah'] = record.lkpp_govt_price
                data_harga['ongkos_kirim'] = 0
                data_harga['kurs_id'] = 1
                data_harga['tanggal_update'] = record.write_date

                # input data to data_product

                data_product['informasi'] = product_informasi
                data_product['spesifikasi'] = product_spesifikasi
                data_product['image'] = data_image
                data_product['harga'] = data_harga
                data_product['lampiran'] = None

            
            data = OrderedDict()
            data['produk'] = data_product
            
        else:
            data = {'error': data_config
            }

        return Response(json.dumps(data), content_type='application/json')
