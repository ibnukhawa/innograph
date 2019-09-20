from odoo import api, fields, models
# add alfif
class SliderBannerSatu(models.Model):
    _name = 'slider.banner_satu'
    # _description = 'New Description'

    image = fields.Binary(string='Image Slider')

class SliderBannerDua(models.Model):
    _name = 'slider.banner_dua'
    # _description = 'New Description'

    image = fields.Binary(string='Image Slider')

class SliderBannerTiga(models.Model):
    _name = 'slider.banner_tiga'
    # _description = 'New Description'

    image = fields.Binary(string='Image Slider')

class SliderTabs(models.Model):
    _name = 'slider.tabs'

    name=fields.Char(string="Name",required="true")
    product_ids = fields.Many2many('product.template',string='Products')
    sequence = fields.Integer(string='Sequence', translate=True)
    is_active = fields.Boolean(string='Active', translate=True)

class SliderCategory(models.Model):
    _name = 'slider.category'

    # Category=fields.One2many('product.public.category',required="true")
    Color=fields.Char(string="Color",required="true")
    image = fields.Binary(string='Icon Image',required="true")
