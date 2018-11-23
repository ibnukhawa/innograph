# -*- coding: utf-8 -*-
from odoo import fields, models, _


class Saleorder(models.Model):
    _inherit = "sale.order"

    registration_source = fields.Char()
    receipt_document = fields.Binary()
