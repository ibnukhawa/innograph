# -*- coding: utf-8 -*-
import math
from odoo import models, fields, api


class ProductTemplate(models.Model):
	_inherit = 'product.template'

	counter_view = fields.Integer(string='Viewer')
	sold_product = fields.Integer(string='Product Sold')
	short_description = fields.Html(string='Deskripsi singkat')
	product_detail = fields.Html(string='Detail Produk')
	installation_instructions = fields.Html(string='Petunjuk Pemasangan')
	product_gallery = fields.Html(string='Galery Produk')
	tab_ids = fields.One2many('product.tab', 'product_id')

	api.multi
	def get_sold_qty(self,qty):
		result = {'qty': '', 'satuan': ''}
		if qty < 1000:
			result['qty'] = str(qty)
		elif qty >= 1000:
			result['qty'] = self.get_data_koma(str(math.floor(qty)/1000))
			result['satuan'] = ' rb'
		elif qty >=1000000:
			result['qty'] = self.get_data_koma(str(math.floor(qty)/1000000))
			result['satuan'] = ' jt'
		else:
			result['qty'] = self.get_data_koma(str(math.floor(qty)/1000000000))
			result['satuan'] = ' m'
		return result

	api.multi
	def get_view_product(self,qty):
		result = {'qty': '', 'satuan': ''}
		if qty < 1000:
			result['qty'] = str(qty)
		elif qty >= 1000:
			result['qty'] = self.get_data_koma(str(math.floor(qty)/1000))
			result['satuan'] = ' rb'
		elif qty >=1000000:
			result['qty'] = self.get_data_koma(str(math.floor(qty)/1000000))
			result['satuan'] = ' jt'
		else:
			result['qty'] = self.get_data_koma(str(math.floor(qty)/1000000000))
			result['satuan'] = ' m'
		return result

	api.multi
	def get_data_koma(self,qty):
		qty = qty.split('.')
		if qty[1][0:1] == str(0):
			return qty[0]
		else:
			return qty[0]+'.'+qty[1][0:2]
