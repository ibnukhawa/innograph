# -*- coding: utf-8 -*-
"""custom_order_pembelian"""
from odoo import fields, exceptions, models, api, _
from odoo.addons.amount_to_text_id.amount_to_text import Terbilang


class PurchaseOrder(models.Model):
    """custom_order_pembelian"""
    _inherit = "purchase.order"

#     project_code =fields.Char(string="Project code")
    approver = fields.Many2one('res.partner', string="Approver")
    is_approver = fields.Boolean(compute='_compute_is_approver')
#     is_creator = fields.Boolean(compute='_compute_is_creator', default=True)

    @api.one
    def _compute_is_approver(self):
        """
        Compute active user same with approver or not
        :return:
        """
        active_user = self.env.user.partner_id.id
        if active_user == self.approver.id:
            self.is_approver = True
        else:
            self.is_approver = False

    @api.multi
    def _current_user(self):
        return self.env.user.id

    @api.one
    def terbilang(self):
        self.amount_text = Terbilang(self.amount_total)

    @api.multi
    def print_purchase_order(self):
        return self.env['report'].get_action(self, 'purchase.report_purchaseorder')

    user_id = fields.Many2one('res.users', string='Contact Person', default=_current_user)
    amount_text = fields.Char(compute='terbilang')

    @api.multi
    def get_tax(self):
        taxes = []
        res = []

        for line in self.order_line:
            for tax in line.taxes_id:
                if tax.id not in taxes:
                    taxes.append(tax.id)
        for i in taxes:
            value = 0
            for line in self.order_line:
                for tax in line.taxes_id:
                    if i == tax.id:
                        value += (tax.amount * line.price_subtotal) / 100
            a = self.env['account.tax'].search([('id', '=', i)])
            res.append({'name': a.name, 'value': value})
        return res

    @api.multi
    def write(self, vals):
        """
        Super function write to only user responsible can edit purchase order
        :return:
        """
        res = super(PurchaseOrder, self).write(vals)
        for purchase in self:
            if self.user_has_groups('purchase.group_purchase_user') and not self.user_has_groups('purchase.group_purchase_manager'):
                if purchase.requisition_id:
                    if purchase.env.user.id not in [purchase.user_id.id, purchase.requisition_id.user_id.id]:
                        raise exceptions.Warning(
                            'Sorry! To Edit this item Please Contact User responsible (%s or %s) for this %s' 
                            % (purchase.user_id.name, purchase.requisition_id.user_id.name, purchase.name))
                else:
                    if purchase.user_id.id != purchase.env.user.id:
                        raise exceptions.Warning(
                            'Sorry! To Edit this item Please Contact User responsible (%s) for this %s' 
                            % (purchase.user_id.name, purchase.name))
        return res

    def get_cure(self):
        return self.currency_id.symbol

    @api.multi
    def button_approve(self):
        """
        Inherit button approve to change the approver when different approver approve the PO
        send email to creator that the PO already approved
        :return:
        """
        res = super(PurchaseOrder, self).button_approve()
        if self.env.user.partner_id != self.approver:
            self.approver = self.env.user.partner_id.id

        for order in self:
            order._send_po_email('custom_order_pembelian.email_po_creator',
                                 order.approver, order.create_uid.partner_id)
        return res

    @api.multi
    def button_confirm(self):
        """
        Overide button confirm that already exist to add when purchase manager confirm PO
        the PO will not auto approved when the active user is not approver
        :return:
        """
        res = True
        for order in self:
            if order.state not in ['draft', 'sent']:
                continue

            order._add_supplier_to_product()
            if self.env.user.id in self.approver.user_ids.ids:
                res = super(PurchaseOrder, self).button_confirm()
            else:
                order.write({'state': 'to approve'})

            order._send_po_email('custom_order_pembelian.email_po_approver',
                                 order.create_uid.partner_id, order.approver)
            user_follow = [1] + order.approver.user_ids.ids
            order.message_subscribe_users(user_ids=user_follow)
        return res

    def _send_po_email(self, template, partner_from, partner_to):
        """
        Send email PO condition approved / to be approved
        :param template: template of email approved/to approved
        :param partner_from: sender of the email
        :param partner_to: receiver of the email
        :return:
        """
        symbol = self.currency_id.symbol
        position = self.currency_id.position

        email = self.env.ref(template)
        email.write({
            'email_to': partner_to.email,
            'email_from': partner_from.email,
        })
        description = []
        for line in self.order_line:
            description.append(line.name)
        first_desc = ""
        if description:
            first_desc = description.pop(0)
        email.with_context(symbol=symbol, position=position, first_desc=first_desc,
                           description=description).send_mail(self.id, force_send=True)


class PurchaseOrderLine(models.Model):
    """custom_order_pembelian"""
    _inherit = "purchase.order.line"

    product_user_id = fields.Many2one('res.partner', string='User')
    account_analytic_id = fields.Many2one('account.analytic.account', string='Project Code')

