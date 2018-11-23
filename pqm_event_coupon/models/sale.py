# -*- coding:utf-8 -*-
from odoo import models, fields, api

class SaleOrder(models.Model):
	_inherit = 'sale.order'

	coupon_id = fields.Many2one('event.coupon', string="Event Coupon")
	amount_discount = fields.Monetary(string="Total Discount", compute="_compute_amount_discount")
	amount_total_origin = fields.Monetary(string="Total", help="Total without Discount", compute="_compute_origin_total")

	@api.multi
	def _compute_origin_total(self):
		for sale in self:
			total = 0
			for line in sale.order_line:
				total += line.price_subtotal_origin
			sale.amount_total_origin = total

	@api.multi
	def _compute_amount_discount(self):
		for sale in self:
			total = 0
			for line in sale.order_line:
				total += line.coupon_value
			sale.amount_discount = total

class SaleOrderLine(models.Model):
	_inherit = 'sale.order.line'

	coupon_id = fields.Many2one('event.coupon', string="Event Coupon", related="order_id.coupon_id")
	coupon_value = fields.Float(string="Coupon Value", compute="_compute_coupon_value")
	price_subtotal_origin = fields.Monetary(string="Subtotal", compute="_compute_subtotal_origin")

	@api.multi
	def _compute_coupon_value(self):
		for line in self:
			value = 0
			if line.coupon_id:
				if line.coupon_id.apply_method == 'fixed':
					value = line.coupon_id.discount_fixed * line.product_uom_qty
					line.discount = 0
				else:
					value = (line.coupon_id.discount_percentage / 100) * line.price_subtotal_origin
			line.coupon_value = value

	@api.multi
	def _compute_subtotal_origin(self):
		for line in self:
			price = line.price_unit * line.product_uom_qty
			line.price_subtotal_origin = price

	@api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id')
	def _compute_amount(self):
		for line in self:
			""" Compute the amounts of the SO line."""
			price = (line.price_unit * (1 - (line.discount or 0.0) / 100.0))
			if line.coupon_id and line.coupon_id.apply_method == 'fixed':
				price = price - (line.product_uom_qty * line.coupon_id.discount_fixed)
			taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty, product=line.product_id, partner=line.order_id.partner_shipping_id)
			line.update(
				{'price_tax': taxes['total_included'] - taxes['total_excluded'],
				'price_total': taxes['total_included'],
				'price_subtotal': taxes['total_excluded'],
			})



