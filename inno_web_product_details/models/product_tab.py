from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ProductTab(models.Model):
    _name = 'product.tab'

    name = fields.Char()
    description = fields.Char()
    product_id = fields.Many2one('product.template')
