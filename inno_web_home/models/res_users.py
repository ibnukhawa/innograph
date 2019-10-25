from odoo import api, fields, models

class WebsiteProductCategory(models.Model):
    _inherit = 'res.users'
    
    product_ids = fields.Many2many('product.template',string='Products')