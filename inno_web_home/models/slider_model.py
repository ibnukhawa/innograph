from odoo import api, fields, models
# add alfif
class SliderBannerSatu(models.Model):
    _name = 'slider.banner_satu'
    # _description = 'New Description'

    image = fields.Binary(string='Image Slider', required=True)
    url = fields.Char(string='Url')
    access_url = fields.Many2one('website.menu.url')

class SliderBannerDua(models.Model):
    _name = 'slider.banner_dua'
    # _description = 'New Description'

    image = fields.Binary(string='Image Slider', required=True)
    url = fields.Char(string='Url')
    access_url = fields.Many2one('website.menu.url')

class SliderBannerTiga(models.Model):
    _name = 'slider.banner_tiga'
    # _description = 'New Description'

    image = fields.Binary(string='Image Slider', required=True)
    url = fields.Char(string='Url')
    access_url = fields.Many2one('website.menu.url')

class SliderTabs(models.Model):
    _name = 'slider.tabs'

    name=fields.Char(string="Name",required="true")
    product_ids = fields.Many2many('product.template',string='Products')
    sequence = fields.Integer(string='Sequence', translate=True)
    is_active = fields.Boolean(string='Active', translate=True)

    access_url = fields.Many2one('website.menu.url')

class SliderCategory(models.Model):
    _name = 'slider.category'

    # Category=fields.One2many('product.public.category',required="true")
    Color=fields.Char(string="Color",required="true")
    image = fields.Binary(string='Icon Image',required="true")

    access_url = fields.Many2one('website.menu.url')

class SliderMultipleCategory(models.Model):
    _name = 'slider.multiple_category'

    category_ids = fields.Many2many('product.public.category',string='Cetegory')
    sequence = fields.Integer(string='Sequence', translate=True)
    is_active = fields.Boolean(string='Active', translate=True)

    access_url = fields.Many2one('website.menu.url')
