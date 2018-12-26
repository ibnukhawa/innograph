# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT

class SaleOrder(models.Model):
    _inherit = "sale.order"
     
    state = fields.Selection([
        ('draft', 'Quotation'),
        ('sent', 'Quotation Sent'),
        ('waiting_for_approval', 'Waiting For Approval'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
        ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')
    approver_id = fields.Many2one('res.users', 'Approver', track_visibility='onchange')
    
    @api.multi
    def action_confirm(self):
        for sale_order in self:
            if not sale_order.approver_id == self.env.user: 
                raise UserError(_('You can not confirm this order. Only selected approver can confirm this order.'))
            approve_discount = False
            for order_line in sale_order.order_line:
                if not order_line.discount <= sale_order.approver_id.sale_order_discount_limit:
                    approve_discount = True
            if approve_discount:
                sale_order.approve_order()
                return True
            elif not sale_order.amount_total <= sale_order.approver_id.sale_order_amount_limit:
                sale_order.approve_order()
                return True
        return super(SaleOrder, self).action_confirm()

    def approve_order(self):
        max_discount = 0
        for order_line in self.order_line:
            if max_discount < order_line.discount:
                max_discount = order_line.discount
        qualified_user = self.env['res.users'].search([
            ('sale_order_amount_limit', '>=', self.amount_total),
            ('sale_order_discount_limit', '>=', max_discount),
            ('sale_order_can_approve', '=', 'yes')], order='sale_order_amount_limit', limit=1)
        if not qualified_user:
            raise UserError('No approver qualified to approve this order. please raise approver limit / set new approver.')
        self.write({'approver_id': qualified_user.id, 'state': 'waiting_for_approval'})