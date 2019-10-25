# -*- coding: utf-8 -*-
from odoo import fields, models


class ResCurrency(models.Model):
    _inherit = 'res.currency'

    lkpp_currency_id = fields.Char()
