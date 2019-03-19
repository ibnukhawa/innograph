# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime, timedelta, date
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    sale_order_id = fields.Many2one('sale.order', string="Sales Order")
    amount_real = fields.Monetary(compute="_compute_amount_real")

    @api.multi
    def _compute_amount_real(self):
        for order in self:
            order.amount_real = order.product_qty * order.price_unit


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    date_confirm = fields.Date(string="Confirm Date")
    amount = fields.Monetary(compute="_compute_amount", help="Amount not include discounts and taxes")
    amount_discount = fields.Monetary(compute="_compute_total_discount")

    @api.multi
    def _compute_amount(self):
        for order in self:
            amounts = order.order_line.mapped('amount_real')
            order.amount = sum(amounts)

    @api.multi
    def _compute_total_discount(self):
        for order in self:
            total_discount = 0
            for line in order.order_line:
                total_discount += (line.discount/100 * line.amount_real)
            order.amount_discount = total_discount

    @api.multi
    def button_confirm(self):
        today = date.today()
        res = super(PurchaseOrder, self).button_confirm()
        alarm_id = self.env.ref('inno_purchase_order.alarm_2_days_before').id
        calendar_event_obj = self.env['calendar.event']
        for order in self:
            order.date_confirm = today
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

    def _is_out_dated(self, date):
    	""" Check if Scheduled Date on Date already passed """
        date_now = datetime.now() + timedelta(days=2)
        date = datetime.strptime(date, DEFAULT_SERVER_DATETIME_FORMAT).date()
        return date_now.date() >= date

    def _get_not_done_picking(self, order):
    	""" Get Not Done or Cancel Transfers of PO """
        return order.picking_ids.filtered(lambda pick: pick.state not in ['done', 'cancel'])

    def check_incoming_shipment(self):
        purchase_orders = self.env['purchase.order'].search([('state', 'in', ['purchase'])])
        email = self.env.ref('inno_purchase_order.purchase_reminder_notification_email')
        for order in purchase_orders.filtered(lambda x:self._is_out_dated(x.date_planned) and len(self._get_not_done_picking(x)) > 0):
            pickings = self._get_not_done_picking(order)
            pickings_name = ', '.join(pickings.mapped('name'))
            # Product Names
            products = ', '.join(order.order_line.mapped('name'))
            # Project
            project = "-"
            project_ids = order.order_line.mapped('account_analytic_id').mapped('project_ids')
            if len(project_ids) > 0:
                project = project_ids[0].name
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
