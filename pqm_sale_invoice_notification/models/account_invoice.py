# -*- coding: utf-8 -*-
"""account invoice"""
from odoo import models, api


class AccountInvoice(models.Model):
    """Inherit model account invoice"""
    _inherit = "account.invoice"

    def action_invoice_open(self):
        res = super(AccountInvoice, self).action_invoice_open()
        if self.state == 'open' and self.type == 'out_invoice':
            self.add_followers()
            self.send_follower_email_open(self.id)
            return res

    def action_invoice_paid(self):
        res = super(AccountInvoice, self).action_invoice_paid()
        if self.state == 'paid' and self.type == 'out_invoice':
            self.send_follower_email_paid(self.id)
            return res

    def get_user_receipt(self):
        users = []
        append = users.append
        admin_user = self.env['res.users'].search([('id', '=', 1)])
        # sale_id = self.env['sale.order'].search([('name', '=', self.origin)])
        append(admin_user)

        # director_user = self.env['res.users'].\
        #     search([('is_director', '=', True)])
        # for director in director_user:
        #     append(director)

        # billing_id = self.env.ref('account.group_account_invoice').id
        # billing_user = self.env['res.users'].\
        #     search([('groups_id', '=', billing_id)])
        # for billing in billing_user:
        #     if billing not in users:
        #         append(billing)

        # for follower in sale_id.project_project_id.message_follower_ids:
        #     if follower.partner_id not in users:
        #         follower_id = self.env['res.users'].\
        #             search([('partner_id', '=', follower.partner_id.id)])
        #         append(follower_id)
        return users

    @api.multi
    def add_followers(self):
        for user in self.get_user_receipt():
            self.message_subscribe_users(user_ids=user.id)

    @api.model
    def send_follower_email_open(self, rec_id):
        """
        send email to follower if the state is open
        """
        sale_id = self.env['sale.order'].search([('name', '=', self.origin)])
        symbol = self.currency_id.symbol
        template_id = self.env.\
            ref('pqm_sale_invoice_notification.invoice_open_email_template')
        for rec in self.get_user_receipt():
            template_id.write({
                'email_to': rec.partner_id.email,
            })
            template_id.\
                with_context(symbol=symbol, receipt=rec.partner_id.name,
                             project_name=sale_id.project_id.code,
                             project_title=sale_id.project_id.name).\
                send_mail(rec_id, force_send=True)

    @api.model
    def send_follower_email_paid(self, rec_id):
        """
        send email to follower if the state is paid
        """
        sale_id = self.env['sale.order'].search([('name', '=', self.origin)])
        symbol = self.currency_id.symbol
        template_id = self.env.\
            ref('pqm_sale_invoice_notification.invoice_paid_email_template')
        for rec in self.get_user_receipt():
            template_id.write({
                'email_to': rec.partner_id.email,
            })
            template_id.\
                with_context(symbol=symbol, receipt=rec.partner_id.name,
                             project_name=sale_id.project_id.code,
                             project_title=sale_id.project_id.name).\
                send_mail(rec_id, force_send=True)
