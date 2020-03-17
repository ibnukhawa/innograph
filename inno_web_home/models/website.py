# -*- coding: utf-8 -*-

from odoo import models, fields
from odoo.http import request


class Website(models.Model):
    _inherit = 'website'

    social_instagram = fields.Char('Instagram Account')