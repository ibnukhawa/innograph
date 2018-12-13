from odoo import api, fields, models
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    discount = fields.Monetary()
    amount = fields.Monetary(compute="_amount_disc_exclude")

    @api.depends('order_line.price_total')
    def _amount_disc_exclude(self):
        amount = 0
        for line in self.order_line:
            if not line.product_id.is_discount:
                amount += line.price_total
        self.amount = amount

    @api.model
    def create(self, vals):
        res = super(SaleOrder, self).create(vals)
        res.compute_global_discount()
        return res

    @api.multi
    def write(self, vals):
        res = super(SaleOrder, self).write(vals)
        for order in self:
            order.compute_global_discount()
        return res

    def compute_global_discount(self):
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
                    self.write({
                        'order_line': [(0, False, {
                            'product_id': disc.id, 
                            'product_uom_qty': 1,
                            'price_unit': - self.discount,
                        })]
                    })
    