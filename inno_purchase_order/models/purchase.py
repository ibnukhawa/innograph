# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

class PurchaseOrderLine(models.Model):
	_inherit = "purchase.order.line"

	sale_order_id = fields.Many2one('sale.order', string="Sales Order")

class PurchaseOrder(models.Model):
	_inherit = "purchase.order"

	@api.multi
	def button_confirm(self):
		res = super(PurchaseOrder, self).button_confirm()
		alarm_id = self.env.ref('inno_purchase_order.alarm_2_days_before').id
		calendar_event_obj = self.env['calendar.event']
		for order in self:
			vals = {
				'name': "Incoming Product For [%s]" % (order.name),
				'start': datetime.strftime(datetime.now(), DEFAULT_SERVER_DATETIME_FORMAT),
				'stop': order.date_planned,
				'allday': True,
				'alarm_ids': [(4, alarm_id)],
				'user_id': order.user_id.id,
				'partner_ids': [(6, 0, [order.user_id.partner_id.id, order.approver.id])]
			}
			new_event = calendar_event_obj.create(vals)
		return res

	def check_incoming_shipment(self):
		now = datetime.strftime(datetime.now(), DEFAULT_SERVER_DATETIME_FORMAT)
		date_now = datetime.now() + timedelta(days=2)
		purchase_orders = self.env['purchase.order'].search([('state', 'in', ['purchase'])])
		email = self.env.ref('inno_purchase_order.purchase_reminder_notification_email')
		for order in purchase_orders.filtered(lambda x:date_now.date() >= datetime.strptime(x.date_planned, DEFAULT_SERVER_DATETIME_FORMAT).date()):
			# Pickings
			pickings = order.picking_ids.filtered(lambda pick:pick.state not in ['done', 'cancel'])
			pickings_name = ', '.join(pickings.mapped('name'))
			# Product Names
			products = ', '.join(order.order_line.mapped('name'))
			# Project 
			projects = order.order_line.mapped('account_analytic_id').mapped('project_ids')
			if len(projects) > 0:
				project = projects[0].name
			# Purchase Amount
			amount = "%s %s" % (order.currency_id.symbol, "{:,.2f}".format(order.amount_total))

			context = {
				'pickings': pickings_name,
				'products': products,
				'project': project,
				'amount': amount
			}
			if order.user_id:
				context['name'] = order.user_id.name
				context['email'] = order.user_id.partner_id.email
				email.with_context(data=context).send_mail(order.id, force_send=True)

			if order.approver:
				context['name'] = order.approver.name
				context['email'] = order.approver.email
				email.with_context(data=context).send_mail(order.id, force_send=True)

