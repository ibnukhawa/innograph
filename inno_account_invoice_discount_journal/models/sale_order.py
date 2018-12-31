from odoo import api, fields, models
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    discount = fields.Monetary()
    amount = fields.Monetary(compute="_amount_disc_exclude")
    # order_line = fields.One2many('sale.order.line', 'order_id',
    #                              string='Order Lines', 
    #                              domain=[('is_product_discount', '=', False)], 
    #                              states={'cancel': [('readonly', True)], 'done': [('readonly', True)]}, 
    #                              copy=True, auto_join=True)

    @api.multi
    @api.depends('order_line.price_total')
    def _amount_disc_exclude(self):
        for order in self:
            amount = 0
            for line in order.order_line:
                if not line.product_id.is_discount:
                    amount += line.price_subtotal
            order.amount = amount

    @api.model
    def create(self, vals):
        res = super(SaleOrder, self).create(vals)
        res.compute_global_discount()
        return res

    @api.multi
    def write(self, vals):
        res = super(SaleOrder, self).write(vals)
        for order in self:
            print (">>>>>>", order)
            if  self._context.get('discount_applied'):
                continue
            print (">> lanjut >>", self._context)
            order.compute_global_discount()
        return res

    def compute_global_discount(self):
        context = self._context.copy()
        if self.discount < 0:
            raise UserError('Discount amount must be greater than 0, %s given' % self.discount)
        disc_line = False
        for line in self.order_line:
            if line.product_id.is_discount:
                if disc_line:
                    line.unlink()
                else:
                    disc_line = line
        
        if self.discount == 0.0 and disc_line:
            disc_line.unlink()
        elif self.discount > 0.0:
            if disc_line:
                disc_line.product_uom_qty = 1
                disc_line.price_unit = - self.discount
            else:
                disc = self.env['product.product'].search([('is_discount', '=', True)], limit=1)
                if not disc:
                    raise UserError("No product identified as discount, please create one")
                else:
                    context['discount_applied'] = True
                    self.with_context(context).write({
                        'order_line': [(0, False, {
                            'product_id': disc.id, 
                            'product_uom_qty': 1,
                            'price_unit': - self.discount,
                        })]
                    })

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    is_product_discount = fields.Boolean(related="product_id.is_discount")
    