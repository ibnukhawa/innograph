# -*- coding: utf-8 -*-
# pylint: disable=import-error,protected-access,too-few-public-methods

"""sale order"""
from odoo import models, api


class SaleOrder(models.Model):
    """Inherit model sale.order"""
    _inherit = "sale.order"

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        if self.state == 'sale':
            self.add_followers()
            self.send_follower_email(self.id)
            return res

    def get_user_receipt(self):
        users = []
        append = users.append
        admin_user = self.env['res.users'].search([('id', '=', 1)])
        append(admin_user)

#         director_user = self.env['res.users'].\
#             search([('is_director', '=', True)])
#         for director in director_user:
#             append(director)
# 
#         billing_id = self.env.ref('account.group_account_invoice').id
#         billing_user = self.env['res.users'].\
#             search([('groups_id', '=', billing_id)])
#         for billing in billing_user:
#             if billing not in users:
#                 append(billing)

#         for follower in self.project_project_id.message_follower_ids:
#             if follower.partner_id not in users:
#                 follower_id = self.env['res.users'].\
#                     search([('partner_id', '=', follower.partner_id.id)])
#                 append(follower_id)
        return users

    @api.multi
    def add_followers(self):
        for user in self.get_user_receipt():
            self.message_subscribe_users(user_ids=user.id)

    @api.model
    def send_follower_email(self, rec_id):
        """
        send email to follower
        """
        template_id = self.env.ref('pqm_sale_invoice_notification.sale_order_email_template')
        symbol = self.currency_id.symbol
        for rec in self.get_user_receipt():
            template_id.write({
                'email_to': rec.partner_id.email,
            })
            template_id.with_context(symbol=symbol, receipt=rec.partner_id.name).\
                send_mail(rec_id, force_send=True)
