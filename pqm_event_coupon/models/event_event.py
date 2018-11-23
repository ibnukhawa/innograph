# -*- coding:utf-8 -*-
from odoo import models, fields, api

class EventEvent(models.Model):
	_inherit = "event.event"

	applicable_coupon = fields.Many2many('event.coupon' ,'event_event_coupon_rel', 'event_id', 'coupon_id', string='Applicable Coupon')