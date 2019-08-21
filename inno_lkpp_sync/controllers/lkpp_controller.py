# -*- coding: utf-8 -*-
import json

import requests

import math

from odoo.http import Controller, Response, request, route

from datetime import datetime, date, timedelta

API = 'https://e-katalog.lkpp.go.id/api/'


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

    @route('/lkpp/all_produk', methods=['GET', 'POST'], type='http', auth='none')
    def lkpp_all_product(self, **kwargs):
        # URL Parameters
        key = kwargs.get('secretkey')
        per_page_url = kwargs.get('per_page', '500')
        per_page = int(per_page_url)
        page_url = kwargs.get('page', '1')
        page = int(page_url)
        order_by = kwargs.get('order_by', 'create_date')
        sort = kwargs.get('sort', 'desc')

        orderby=order_by+" "+sort
        
        data_product = []
        data_config=request.env['ir.config_parameter'].sudo().get_param('lkpp.secretkey', default='')
        
        if data_config == key:
            records = request.env['product.template'].sudo().search([],offset=page, limit=per_page,order=orderby)
            total = records.search_count([])

            total_page = math.ceil(total/per_page)
            for record in records:
                print(str(record.default_code))
                url_produk='http://localhost:8069/shop/product/'+str(record.id)
                url_50='http://localhost:8069/web/image/product.template/'+str(record.id)+'/image/50x50'
                url_100='http://localhost:8069/web/image/product.template/'+str(record.id)+'/image/100x100'
                url_300='http://localhost:8069/web/image/product.template/'+str(record.id)+'/image/300x300'
                url_800='http://localhost:8069/web/image/product.template/'+str(record.id)+'/image/800x800'
                product_informasi=({
                    'unspsc':record.unspsc,
                    'id_kategori_produk_lkpp':record.lkpp_category_id,
                    'nama_produk':record.name,
                    'no_produk_penyedia':record.default_code,
                    'id_manufaktur':record.lkpp_manufacturer_id,
                    'id_unit_pengukuran_lkpp':False,
                    'deskripsi_singkat':record.description_sale,
                    'deskripsi_lengkap':record.description_sale,
                    'kuantitas_stok':record.qty_available,
                    'tanggal_update':record.write_date,
                    'produk_aktif':record.active_product,
                    'apakah_produk_lokal':record.local_product,
                    'berlaku_sampai':record.valid_date,
                    'url_produk':url_produk,
                    'image_50x50':url_50,
                    'image_100x100':url_100,
                    'image_300x300':url_300,
                    'image_800x800':url_800,
                })

                attribute=[]

                product_variants=request.env['product.attribute'].search([('attribute_line_ids.product_tmpl_id', '=', record.id)])

                for attr in product_variants:
                    deskripsi = ""
                    for value in attr.value_ids:
                        deskripsi = deskripsi +" "+value.name

                    attribute.append({
                        'label': attr.name,
                        'deskripsi': deskripsi
                    })

                product_spesifikasi=({
                    'item':attribute,
                    'tanggal_update':record.write_date
                })

                image=({
                    'deskripsi':record.description_sale,
                    'image_50x50':url_50,
                    'image_100x100':url_100,
                    'image_300x300':url_300,
                    'image_800x800':url_800,
                })

                data_image=({
                    'item':image,
                    'tanggal_update':record.write_date
                })

                data_harga=({
                    'harga_retail':record.lkpp_sell_price,
                    'harga_pemerintah':record.lkpp_govt_price,
                    'ongkos_kirim':False,
                    'kurs_id':False,
                    'tanggal_update':record.write_date,
                })

                data_product.append({
                    'informasi':product_informasi,
                    'spesifikasi':product_spesifikasi,
                    'image':data_image,
                    'harga':data_harga,
                    'lampiran':False
                })   

            data = {'total': total,
                'current_page': page,
                'per_page': per_page,
                'total_page': total_page,
                'produk':data_product
            }
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
        print(start_date)
        print(end_date)

        # domain=[
        #         ('write_date','>',start_date),
        #         ('write_date','<',end_date)
        #     ]

        orderby=order_by+" "+sort
        
        data_product = []
        data_config=request.env['ir.config_parameter'].sudo().get_param('lkpp.secretkey', default='')
        
        if data_config == key:
            
            # records = request.env['product.template'].sudo().search(domain,offset=page, limit=per_page,order=orderby)
            
            query="SELECT * from product_template where to_char(write_date, 'yyyy-mm-dd HH24:MI:SS') BETWEEN '"+str(start_date)+"' and '"+str(end_date)+"' order by "+orderby+" OFFSET "+str((page-1)*per_page)+" LIMIT "+str(per_page)
            print(query)
            print(query)
            records = request.env.cr.execute(query)

            
            res = request.env.cr.dictfetchall()
            total = len(res)

            total_page = math.ceil(total/per_page)
            for record in res:

                url_produk='http://localhost:8069/shop/product/'+str(record.id)
                url_50='http://localhost:8069/web/image/product.template/'+str(record.id)+'/image/50x50'
                url_100='http://localhost:8069/web/image/product.template/'+str(record.id)+'/image/100x100'
                url_300='http://localhost:8069/web/image/product.template/'+str(record.id)+'/image/300x300'
                url_800='http://localhost:8069/web/image/product.template/'+str(record.id)+'/image/800x800'
                
                product_informasi=({
                    'unspsc':record['unspsc'],
                    'id_kategori_produk_lkpp':record['lkpp_category_id'],
                    'nama_produk':record['name'],
                    'no_produk_penyedia':record.default_code,
                    'id_manufaktur':record['lkpp_manufacturer_id'],
                    'id_unit_pengukuran_lkpp':False,
                    'deskripsi_singkat':record['description_sale'],
                    'deskripsi_lengkap':record['description_sale'],
                    'kuantitas_stok':record.qty_available,
                    'tanggal_update':record['write_date'],
                    'produk_aktif':record['active_product'],
                    'apakah_produk_lokal':record['local_product'],
                    'berlaku_sampai':record['valid_date'],
                    'url_produk':url_produk,
                    'image_50x50':url_50,
                    'image_100x100':url_100,
                    'image_300x300':url_300,
                    'image_800x800':url_800,
                })

                attribute=[]

                product_variants=request.env['product.attribute'].search([('attribute_line_ids.product_tmpl_id', '=', record['id'])])

                for attr in product_variants:
                    deskripsi = ""
                    for value in attr.value_ids:
                        deskripsi = deskripsi +" "+value.name

                    attribute.append({
                        'label': attr.name,
                        'deskripsi': deskripsi
                    })

                product_spesifikasi=({
                    'item':attribute,
                    'tanggal_update':record['write_date']
                })

                image=({
                    'deskripsi':record['description_sale'],
                    'image_50x50':url_50,
                    'image_100x100':url_100,
                    'image_300x300':url_300,
                    'image_800x800':url_800,
                })

                data_image=({
                    'item':image,
                    'tanggal_update':record['write_date']
                })

                data_harga=({
                    'harga_retail':record['lkpp_sell_price'],
                    'harga_pemerintah':record['lkpp_govt_price'],
                    'ongkos_kirim':False,
                    'kurs_id':False,
                    'tanggal_update':record['write_date'],
                })

                data_product.append({
                    'informasi':product_informasi,
                    'spesifikasi':product_spesifikasi,
                    'image':data_image,
                    'harga':data_harga,
                    'lampiran':False
                })   

            data = {'total': total,
                'current_page': page,
                'per_page': per_page,
                'total_page': total_page,
                'produk':data_product
            }
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

        data_product = []
        data_config=request.env['ir.config_parameter'].sudo().get_param('lkpp.secretkey', default='')
        
        if data_config == key:
            records = request.env['product.template'].sudo().search([('default_code','=',no_produk_penyedia)])
            
            for record in records:
                
                url_produk='http://localhost:8069/shop/product/'+str(record.id)
                url_50='http://localhost:8069/web/image/product.template/'+str(record.id)+'/image/50x50'
                url_100='http://localhost:8069/web/image/product.template/'+str(record.id)+'/image/100x100'
                url_300='http://localhost:8069/web/image/product.template/'+str(record.id)+'/image/300x300'
                url_800='http://localhost:8069/web/image/product.template/'+str(record.id)+'/image/800x800'
                
                product_informasi=({
                    'unspsc':record.unspsc,
                    'id_kategori_produk_lkpp':record.lkpp_category_id,
                    'nama_produk':record.name,
                    'no_produk_penyedia':record.default_code,
                    'id_manufaktur':record.lkpp_manufacturer_id,
                    'id_unit_pengukuran_lkpp':False,
                    'deskripsi_singkat':record.description_sale,
                    'deskripsi_lengkap':record.description_sale,
                    'kuantitas_stok':record.qty_available,
                    'tanggal_update':record.write_date,
                    'produk_aktif':record.active_product,
                    'apakah_produk_lokal':record.local_product,
                    'berlaku_sampai':record.valid_date,
                    'url_produk':url_produk,
                    'image_50x50':url_50,
                    'image_100x100':url_100,
                    'image_300x300':url_300,
                    'image_800x800':url_800,
                })

                attribute=[]

                product_variants=request.env['product.attribute'].search([('attribute_line_ids.product_tmpl_id', '=', record.id)])

                for attr in product_variants:
                    deskripsi = ""
                    for value in attr.value_ids:
                        deskripsi = deskripsi +" "+value.name

                    attribute.append({
                        'label': attr.name,
                        'deskripsi': deskripsi
                    })

                product_spesifikasi=({
                    'item':attribute,
                    'tanggal_update':record.write_date
                })

                image=({
                    'deskripsi':record.description_sale,
                    'image_50x50':url_50,
                    'image_100x100':url_100,
                    'image_300x300':url_300,
                    'image_800x800':url_800,
                })

                data_image=({
                    'item':image,
                    'tanggal_update':record.write_date
                })

                data_harga=({
                    'harga_retail':record.lkpp_sell_price,
                    'harga_pemerintah':record.lkpp_govt_price,
                    'ongkos_kirim':False,
                    'kurs_id':False,
                    'tanggal_update':record.write_date,
                })

                data_product.append({
                    'informasi':product_informasi,
                    'spesifikasi':product_spesifikasi,
                    'image':data_image,
                    'harga':data_harga,
                    'lampiran':False
                })   

            data = {
                'produk':data_product
            }
        else:
            data = {'error': data_config
            }

        return Response(json.dumps(data), content_type='application/json')
