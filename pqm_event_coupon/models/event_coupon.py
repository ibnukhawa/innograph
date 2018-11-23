# -*- coding:utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime
import string
import random
import pytz

class EventCoupon(models.Model):
	_name = "event.coupon"

	_sql_constraints = [
		('name_uniq', 'unique (code)', "Code already exists !"),
	]

	def get_default_code(self):
		size = 5
		chars = string.ascii_uppercase + string.digits
		return ''.join(random.choice(chars) for _ in range(size))

	name = fields.Char()
	image = fields.Binary(string="Coupon Image", attachment=True)
	event_ids = fields.Many2many('event.event' ,'event_event_coupon_rel', 'coupon_id', 'event_id', string='Events')
	apply_method = fields.Selection([('fixed', 'Fixed'), ('percent', 'Percentage')], string="Apply Method", default='percent')
	discount_percentage = fields.Float(string="Discount")
	discount_fixed = fields.Float(string="Discount")
	code = fields.Char(string="Coupon Code", default=get_default_code)
	active = fields.Boolean(default=True)
	limit = fields.Integer(string="User Limit")
	limit_available = fields.Integer(string="Available Limit", compute="_compute_limit_available", store=True)
	limit_usage = fields.Integer(string="Used Limit", compute="_compute_limit_usage", store=True)
	coupon_usage_ids = fields.One2many('event.coupon.usage', 'coupon_id', string="Usage")
	date_begin = fields.Datetime(string="Date Begin", default=datetime.now())
	date_end = fields.Datetime(string="Date End", default=datetime.now())
	state = fields.Selection([('draft', 'Draft'), 
							   ('none', 'Not Available'), 
							   ('available', 'Available'),
							   ('end', 'Ended')
							   ], readonly=True, store=True, copy=False, index=True, track_visibility='onchange', default='draft', compute='_compute_coupon_status')
	minimum_order = fields.Integer(string='Minimum Order', default='1')
	@api.multi
	@api.depends('coupon_usage_ids')
	def _compute_limit_usage(self):
		for coupon in self:
			coupon.limit_usage = len(coupon.coupon_usage_ids)

	@api.multi
	@api.depends('limit', 'limit_usage')
	def _compute_limit_available(self):
		for coupon in self:
			coupon.limit_available = coupon.limit - coupon.limit_usage

	@api.multi
	@api.depends('limit', 'limit_available', 'date_begin', 'date_end')
	def _compute_coupon_status(self):
		for coupon in self:
			status = 'draft'
			now = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")
			print (">>>>", now)
			print (">>>>", coupon.date_end)
			print (">>>>", coupon.date_end < now)
			if coupon.date_begin == coupon.date_end:
				status = 'draft'
			elif coupon.date_end < now:
				status = 'end'
			elif coupon.limit_available == 0 and now > coupon.date_begin and now < coupon.date_end:
				status = 'none'
			elif coupon.limit_available > 0 and now > coupon.date_begin and now < coupon.date_end:
				status = 'available'
			print (">>>>>>>>>>>>>>>>", status)
			coupon.state = status

	def get_coupon_code(self):
		size = 5
		chars = string.ascii_uppercase + string.digits
		self.code = ''.join(random.choice(chars) for _ in range(size))

	def _get_date(self):
		tz = pytz.timezone('Asia/Jakarta')
		user = self.env.user
		if user.tz:
			tz = user.tz
		date_begin = fields.Datetime.from_string(self.date_begin).replace(tzinfo=pytz.utc).astimezone(pytz.timezone(tz or 'UTC'))
		date_end = fields.Datetime.from_string(self.date_end).replace(tzinfo=pytz.utc).astimezone(pytz.timezone(tz or 'UTC'))
		periode = ""
		if date_begin.strftime('%Y%m%d') == date_end.strftime('%Y%m%d'):
			periode = date_end.strftime('%Y-%m-%d')
		elif date_begin.strftime('%Y%m') == date_end.strftime('%Y%m'):
			periode = date_begin.strftime('%d')
			periode = "%s - %s" % (periode, date_end.strftime('%d %b %Y'))
		elif date_begin.strftime('%Y') == date_end.strftime('%Y'):
			periode = date_begin.strftime('%d %b')
			periode = "%s - %s" % (periode, date_end.strftime('%d %b %Y'))
		else:
			periode = date_begin.strftime('%d %b %Y')
			periode = "%s - %s" % (periode, date_end.strftime('%d %b %Y'))
		return periode



class EventCouponUsage(models.Model):
	_name = "event.coupon.usage"

	user_id = fields.Many2one('res.users', string="User")
	coupon_id = fields.Many2one('event.coupon', string="Coupon")
	event_id = fields.Many2one('event.event', string="Event")
	order_id = fields.Many2one('sale.order', string="Order")
