# pylint: disable=C0111,C0303,I0011,R0903
# -*- coding: utf-8 -*-
"""iherit account invoice"""
from odoo import api, fields, models

class AccountJournal(models.Model):
    """account.journal class"""
    _inherit = "account.journal"

    discount_account_id = fields.Many2one('account.account', string='Discount Account', \
        domain=[('deprecated', '=', False)], \
        help="It will use when create journal invoice with discount")
