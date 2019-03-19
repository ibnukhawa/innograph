# -*- coding: utf-8 -*-
""" pqm_account_invoice_discount """
from odoo import api, models, _
from odoo.exceptions import UserError

class SaleOrderLine(models.Model):
    """ Class Sale Order Line """
    _inherit = "sale.order.line"

    @api.multi
    def _prepare_invoice_line(self, qty):
        """prepare to generate invoice line"""
        res = super(SaleOrderLine, self)._prepare_invoice_line(qty)
        if self.order_id.project_id.project_type_id:
            discount = self.order_id.project_id.project_type_id.discount_account_id.id
            if self.discount and not discount:
                raise UserError(_('Please set discount account on Project Type  %s.' % self.order_id.project_id.project_type_id.name))
            res.update({'discount_account_id': discount
                       })
        return res
