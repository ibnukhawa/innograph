# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.addons.sale.models.sale import SaleOrder as SO

class SaleOrder(models.Model):
    _inherit = "sale.order"

    approver_id = fields.Many2one('res.users', 'Approver', track_visibility='onchange', default=False)
    is_need_approval = fields.Boolean('Need Approval', store=True, compute="_compute_need_approval")

    @api.onchange('amount', 'order_line.discount', 'is_need_approval')
    def _onchange_order_discount(self):
        discount = 0
        discount_list = self.order_line.mapped('discount')
        if any(discount_list):
            discount = max(discount_list)

        user_approval = self.env['res.users'].search([('sale_order_can_approve', '=', 'yes'), 
                                                      ('sale_order_discount_limit', '>=', discount)])
        return {'domain' : {'approver_id': [('id', 'in', user_approval._ids)]}}


    @api.multi
    @api.depends('amount', 'order_line.discount')
    def _compute_need_approval(self):
        for sale in self:
            user = self.env.user
            if sale.user_id:
                user = sale.user_id
            
            if not user.sale_order_can_approve:
                sale.approver_id = False
                sale.is_need_approval = True
            else:
                discount_list = sale.order_line.mapped('discount')
                discount = 0
                if any(discount_list):
                    discount = max(discount_list)

                if discount > user.sale_order_discount_limit:
                    sale.approver_id = False
                    sale.is_need_approval = True
                else:
                    sale.approver_id = False
                    sale.is_need_approval = False

    
    @api.multi
    def action_confirm(self):
        return self.before_action_confirm()

    # action_confirm patching.
    # hate this kind of patching. weird, dirty, prone to error!!!
    def before_action_confirm(self):
        error = [
            'Your approval limit is lesser then sale order total amount.Click on "Ask for Approval" for Higher value.',
            'You can not confirm this sale order. You have asked for Higher value.'
        ]
        for sale_order in self.filtered(lambda x:x.is_need_approval):
            approval = sale_order.approval_check()
            if approval:
                return approval
        res = False
        try:
            res = super(SaleOrder, self).action_confirm()           
        except UserError, e:
            if e.name in error:
                SO.action_confirm(self)
        return res

    def approval_check(self):
        if not self.approver_id == self.env.user: 
            raise UserError(_('You can not confirm this order. Only selected approver can confirm this order.'))
        approve_discount = False
        for order_line in self.order_line:
            if not order_line.discount <= self.approver_id.sale_order_discount_limit:
                approve_discount = True
        if approve_discount:
            self.approve_order()
            return True
        elif not self.amount_total <= self.approver_id.sale_order_amount_limit:
            SO.action_confirm(self)
            return True
    
    def approve_order(self):
        max_discount = 0
        for order_line in self.order_line:
            if max_discount < order_line.discount:
                max_discount = order_line.discount
        qualified_user = self.env['res.users'].search([
            ('sale_order_discount_limit', '>=', max_discount),
            ('sale_order_can_approve', '=', 'yes')], order='sale_order_amount_limit', limit=1)
        if not qualified_user:
            raise UserError('No approver qualified to approve this order. please raise approver limit / set new approver.')
        self.write({'approver_id': qualified_user.id, 'state': 'waiting_for_approval'})


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
     
    @api.onchange('discount')
    def onchang_discount_validate(self):
        return {'value': {
            'discount': self.discount
        }}