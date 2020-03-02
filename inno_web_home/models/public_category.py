
from odoo import api, fields, models

class WebsiteProductCategory(models.Model):
    _inherit = 'product.public.category'
    
    description = fields.Html('Description for Category', translate=True)
    # add alfif
    background_color = fields.Char(string='Background Color')
    show_in_website = fields.Boolean(string='Show in Website', translate=True)

    access_url = fields.Many2many('website.menu.url')


       

