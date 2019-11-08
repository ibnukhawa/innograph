# -*- coding: utf-8 -*-
from odoo import api, fields, models


class WebsiteMenuUrl(models.Model):
    _name = 'website.menu.url'

    name = fields.Char()
    url = fields.Char()
    logo = fields.Binary()