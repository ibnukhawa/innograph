# -*- coding: utf-8 -*-
from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    date_scheduled = fields.Datetime(string="Scheduled Date")
    file_id = fields.Binary(string="File Name")
    file_name = fields.Char(string="File Name")
    size_image = fields.Char(string="Image Size")
    size_frame = fields.Char(string="Frame Size")
    size_print = fields.Char(string="Print Size")
    finishing = fields.Char()
    packing = fields.Char()
    finishing_note = fields.Text(string="Note")
    proof = fields.Char()

    @api.multi
    def action_confirm(self):
        ctx = self.env.context.copy()
        for order in self:
            ctx['default_sale_id'] = order.id
            return super(SaleOrder, order.with_context(ctx)).action_confirm()


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.model
    def _get_default_route(self):
        mto_mts_route = self.env.ref('stock_mts_mto_rule.route_mto_mts', raise_if_not_found=False)
        buy_route = self.env.ref('purchase.route_warehouse0_buy', raise_if_not_found=False)
        default_route = mto_mts_route.ids + buy_route.ids
        if mto_mts_route:
            return default_route
        return []

    route_ids = fields.Many2many(default=lambda self: self._get_default_route())


