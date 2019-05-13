# -*- coding: utf-8 -*-
""" Import """
from odoo import models, fields


class StockPicking(models.Model):
    """ Inherit Stock Picking """
    _inherit = "stock.picking"

    sale_order_id = fields.Many2one('sale.order', string="Sale Order")

