# -*- coding:utf-8 -*-
from odoo import models, fields, api, tools
from datetime import datetime
from calendar import monthrange
from odoo.tools.translate import html_translate
import odoo.addons.decimal_precision as dp
import pytz
import os
import re

class EventTarget(models.Model):
	_name = "event.target"

	name = fields.Char(required=True)
	code = fields.Char(required=True)
	event_ids = fields.Many2many('event.event', 'events_targets_rel',
		'target_id', 'event_id', 'Events')

class EventRegistration(models.Model):
	_inherit = "event.registration"

	contact_id = fields.Many2one('res.partner')

	@api.model
	def create(self, vals):
		res = super(EventRegistration, self).create(vals)
		if res.email:
			contact = self.env['res.partner'].search([('email', '=', res.email)], limit=1)
			if not contact:
				parent = res.partner_id.parent_id
				contact = self.env['res.partner'].create({
					'name': res.name,
					'email': res.email,
					'phone': res.phone,
					'parent_id': parent.id if parent else False,
					'type': 'contact',
					'customer': True,
				})
			res.contact_id = contact.id
		return res

class EventFacilitator(models.Model):
	_name = "event.facilitator"

	event_id = fields.Many2one('event.event', string="Event")
	partner_id = fields.Many2one('res.partner', string="Facilitator")
	partner_name = fields.Char(string="Facilitator Name")
	partner_phone = fields.Char()
	partner_email = fields.Char()

	@api.multi
	@api.onchange('partner_id')
	def _onchange_partner_id(self):
		for facilitator in self:
			if facilitator.partner_id:
				facilitator.partner_name = facilitator.partner_id.name
				if facilitator.partner_id.phone:
					facilitator.partner_phone = facilitator.partner_id.phone
				if facilitator.partner_id.email:
					facilitator.partner_email = facilitator.partner_id.email

class EventComment(models.Model):
	""" Comment at event """
	_name = 'event.comment'

	event_id = fields.Many2one('event.event', string="Event")
	user_id = fields.Many2one('res.users', string="Commentator")
	name = fields.Char(related="user_id.name")
	email = fields.Char(related="user_id.login")
	comment = fields.Text()
	publish = fields.Boolean(string="Is Published", default=False)
	reply_id = fields.Many2one('event.comment', string="Reply")

	def set_publish(self):
		if not self.publish:
			self.publish = True
		else:
			self.publish = False

	def reply_comment(self):
		self.ensure_one()
		ir_model_data = self.env['ir.model.data']
		wizard_id = ir_model_data.get_object_reference('pqm_event_core', 'event_comment_reply_wizard')[1]
		context = {
			'default_comment_id': self.id,
		}
		return {
			'type': 'ir.actions.act_window',
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'event.comment.reply',
			'view_id': wizard_id,
			'target': 'new',
			'context': context,
		}

class EventTicket(models.Model):
	_inherit = 'event.event.ticket'

	is_display_price = fields.Boolean(string="Display Price", help="Display price on Website", default=False)	

class EventEvent(models.Model):
	_inherit = "event.event"

	image = fields.Binary(string="Logo", attachment=True)
	facilitator_ids = fields.One2many('event.facilitator', 'event_id', string="Event Facilitators")
	comment_ids = fields.One2many('event.comment', 'event_id', string="Event Comments")
	event_target_ids = fields.Many2many('event.target', 'events_targets_rel', 
		'event_id', 'target_id', 'Event Targets', help="Target attendance of Event.")
	
	comment_count = fields.Integer("Count Comments", compute="_get_comment_count")
	display_price = fields.Float(digits=dp.get_precision('Product Price'), compute='_compute_display_price')

	# Category Project SME
	project_id = fields.Many2one('project.project', string="Project")
	project_sme_id = fields.Many2one('project.sme', string="Category SME", related="project_id.sme_id")
	project_sub_sme_id = fields.Many2one('project.sub.sme', string="Category Sub SME", related="project_id.sub_sme_id")

	attachment_ids = fields.One2many('ir.attachment', compute="_compute_attachment_ids")
	second_description = fields.Html(string='Secondary Description', translate=html_translate, sanitize_attributes=False, readonly=False)

	def google_map_img(self, zoom=8, width=298, height=298):
		res = super(EventEvent, self).google_map_img(zoom, width, height)
		maps_api_key = self.env['ir.config_parameter'].sudo().get_param('google_maps_api_key')
		res = False
		if self.address_id and maps_api_key:
			address = '%s, %s %s, %s' % (self.address_id.street or '', self.address_id.city or '', self.address_id.zip or '', self.address_id.country_id and self.address_id.country_id.name_get()[0][1] or '')
			res = """
			<div id="event_map" style="height:298px"></div>
			<script src="https://maps.googleapis.com/maps/api/js?key=%s"></script>
			<script>
			google.maps.event.addDomListener(window, "load", function(){
				var map = new google.maps.Map(document.getElementById("event_map"), {
					center: new google.maps.LatLng(-6.1756727,106.8549443),
					zoom: 11,
					mapTypeId: google.maps.MapTypeId.ROADMAP,
					mapTypeControl: false,
					scaleControl: false,
					streetViewControl: false,
				});
				var geocoder = new google.maps.Geocoder();
				geocoder.geocode({ 'address': '%s'}, function(results, status){
					if (status == google.maps.GeocoderStatus.OK){
						map.setCenter(results[0].geometry.location);
						var marker = new google.maps.Marker({
							map: map,
							position: results[0].geometry.location
						});
					} else {
						console.log('geocode load failed: ' + status);
					}
				});
			});
			</script>
			""" % (maps_api_key, address)
		return res


	def _description_empty(self):
		res = re.sub('<[^<]+?>', '', self.description).strip()
		return res == ""
	
	def _compute_attachment_ids(self):
		domain = [
			('res_model', '=', self._inherit),
			('res_id', '=', self.id)
		]
		attachments = self.env['ir.attachment'].search(domain)
		self.attachment_ids = attachments.ids


	def _get_comment_count(self):
		self.comment_count = len(self.comment_ids.filtered(lambda x:not x.reply_id))

	@api.multi
	def _compute_display_price(self):
		for event in self:
			display_price = 0.0
			if event.event_ticket_ids:
				if any(event.event_ticket_ids.mapped('is_display_price')):
					display_price = event.event_ticket_ids.filtered(lambda r: r.is_display_price)
				else:
					display_price = event.event_ticket_ids
				display_price = max(display_price.mapped('price'))
			event.display_price = display_price

	def _card_date(self):
		res = ""
		date_begin = fields.Datetime.from_string(self.date_begin).replace(tzinfo=pytz.utc).astimezone(pytz.timezone(self.date_tz or 'UTC'))
		date_end = fields.Datetime.from_string(self.date_end).replace(tzinfo=pytz.utc).astimezone(pytz.timezone(self.date_tz or 'UTC'))
		if date_begin.strftime('%Y%m%d') == date_end.strftime('%Y%m%d'):
			res = date_begin.strftime("%d %b %Y")
		elif date_begin.strftime('%Y%m') == date_end.strftime("%Y%m"):
			res = date_begin.strftime('%d')
			res = "%s - %s" % (res, date_end.strftime('%d %b %Y'))
		elif date_begin.strftime('%Y') == date_end.strftime('%Y'):
			res = date_begin.strftime('%d %b')
			res = "%s - %s" % (res, date_end.strftime('%d %b %Y'))
		else:
			res = date_begin.strftime('%d %b %Y')
			res = "%s - %s" % (res, date_end.strftime('%d %b %Y'))
		return res

	def _card_day(self):
		date = fields.Datetime.from_string(self.date_begin).replace(tzinfo=pytz.utc).astimezone(pytz.timezone(self.date_tz or 'UTC'))
		return date.strftime('%A')

	def _calendar_month(self):
		return [x for x in range(1, 13)]

	def _calendar_schedule(self):
		months = self._calendar_month()
		today = datetime.now()
		schedule = {}
		for month in months:
			date_begin = fields.Datetime.from_string(self.date_begin).replace(tzinfo=pytz.utc).astimezone(pytz.timezone(self.date_tz or 'UTC'))
			date_end = fields.Datetime.from_string(self.date_end).replace(tzinfo=pytz.utc).astimezone(pytz.timezone(self.date_tz or 'UTC'))
			if date_begin.month == month and date_end.month == month:
				schedule[month] =  "%02d - %02d" % (date_begin.day, date_end.day)
			elif date_begin.month != month and date_end.month == month:
				schedule[month] =  "%02d - %02d" % (1, date_end.day)		
			elif date_begin.month == month and date_end.month != month:
				schedule[month] =  "%02d - %02d" % (date_begin.day, monthrange(date_begin.year, month)[1])
		return schedule

	def _event_date_begin(self):
		date = fields.Datetime.from_string(self.date_begin).replace(tzinfo=pytz.utc).astimezone(pytz.timezone(self.date_tz or 'UTC'))
		return date.strftime('%d %b %Y')
	
	def _event_date_end(self):
		date = fields.Datetime.from_string(self.date_end).replace(tzinfo=pytz.utc).astimezone(pytz.timezone(self.date_tz or 'UTC'))
		return date.strftime('%d %b %Y')
	
	def _event_time_from(self):
		date = fields.Datetime.from_string(self.date_begin).replace(tzinfo=pytz.utc).astimezone(pytz.timezone(self.date_tz or 'UTC'))
		return date.strftime('%H:%M')
	
	def _event_time_to(self):
		date = fields.Datetime.from_string(self.date_end).replace(tzinfo=pytz.utc).astimezone(pytz.timezone(self.date_tz or 'UTC'))
		return date.strftime('%H:%M')

	def _event_past(self):
		domain = [
			('state', '=', 'confirm'), 
			('website_published', '=', True),
			('date_begin', '<=', self.date_begin), 
		]
		events = self.sudo().search(domain, order="date_begin desc, id asc", limit=10)
		event_ids = events.ids
		event = False
		for key in range(len(event_ids)):
			if event_ids[key] == self.id:
				if key+1 <= len(event_ids)-1:
					event = events.filtered(lambda r: r.id == event_ids[key+1])
					break
		return event

	def _event_next(self):
		domain = [
			('state', '=', 'confirm'), 
			('website_published', '=', True),
			('date_begin', '>=', self.date_begin), 
		]
		events = self.sudo().search(domain, order="date_begin asc, id desc", limit=10)
		event_ids = events.ids
		event = False
		for key in range(len(event_ids)):
			if event_ids[key] == self.id:
				if key+1 <= len(event_ids)-1:
					event = events.filtered(lambda r: r.id == event_ids[key+1])
					break
		return event

	def _event_related(self):
		domain = [
			('state', '=', 'confirm'), 
			('website_published', '=', True),
			('project_sub_sme_id', '=', self.project_sub_sme_id.id),
			('id', '!=', self.id),
		]
		events = self.sudo().search(domain)
		events = events.filtered(lambda r: r._is_event_registrable())
		return events[:4]

	def _remove_extension_file(self, name):
		filename, extension = os.path.splitext(name)
		return filename