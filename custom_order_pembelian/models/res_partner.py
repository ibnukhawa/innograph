# -*- coding: utf-8 -*-
"""custom_order_pembelian"""
from odoo import models, fields


class ResPartner(models.Model):
    _name = 'res.partner'
    _inherit = "res.partner"

    is_approval = fields.Boolean()
    digital_signature = fields.Binary(string="Digital Signature")
