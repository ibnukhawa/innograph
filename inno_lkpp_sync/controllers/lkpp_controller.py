# -*- coding: utf-8 -*-
import json

import requests

from odoo.http import Controller, Response, request, route

API = 'https://e-katalog.lkpp.go.id/api/'


class LKPPController(Controller):
    """ Controller for JSON, switch the type between 'http' and 'json' if trouble happens. """

    @route('/lkpp/all_produk', methods=['GET', 'POST'], type='http', auth='none')
    def lkpp_all_product(self, **kwargs):
        # URL Parameters
        key = kwargs.get('secretkey')
        # per_page = kwargs.get('per_page', 500)
        # page = kwargs.get('page', 1)
        # order_by = kwargs.get('order_by', 'create_date')
        # sort = kwargs.get('sort', 'desc')

        request.env['ir.config_parameter'].sudo().get_param('lkpp.secretkey', default='')

        data = {'key': key}

        return Response(json.dumps(data), content_type='application/json')


    @route('/lkpp/updated_produk', methods=['GET', 'POST'], type='http', auth='none')
    def lkpp_updated_product(self, **kwargs):
        # URL Parameters
        key = kwargs.get('secretkey')
        # per_page = kwargs.get('per_page', 500)
        # page = kwargs.get('page', 1)
        # start_date = kwargs.get('start_date')
        # end_date = kwargs.get('end_date')
        # order_by = kwargs.get('order_by', 'create_date')
        # sort = kwargs.get('sort', 'desc')

        request.env['ir.config_parameter'].sudo().get_param('lkpp.secretkey', default='')

        data = {'key': key}

        return Response(json.dumps(data), content_type='application/json')


    @route('/lkpp/produk', methods=['GET', 'POST'], type='http', auth='none')
    def lkpp_product(self, **kwargs):
        # URL Parameters
        key = kwargs.get('secretkey')
        # no_produk_penyedia = kwargs.get('no_produk_penyedia')

        # if not no_produk_penyedia:
        #     return Response('No. produk penyedia tidak valid!', status=400)

        request.env['ir.config_parameter'].sudo().get_param('lkpp.secretkey', default='')

        data = {'key': key}

        return Response(json.dumps(data), content_type='application/json')
