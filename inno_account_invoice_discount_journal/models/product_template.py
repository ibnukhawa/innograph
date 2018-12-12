from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_discount = fields.Boolean('Discount')

    @api.onchange('is_discount')
    def is_discount_changed(self):
        if self.is_discount:
            self.type = 'service'