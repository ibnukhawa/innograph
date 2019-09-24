# -*- coding: utf-8 -*-

from odoo import models, fields


class WebsiteConfigSettings(models.TransientModel):
    _inherit = 'website.config.settings'

    social_instagram = fields.Char('Instagram Account', related='website_id.social_instagram')
