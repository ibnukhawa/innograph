# -*- coding: utf-8 -*-
# pylint: disable=import-error,protected-access,too-few-public-methods

"""res users"""
from odoo import fields, models


class ResUsers(models.Model):
    """Inherit model res.users"""
    _inherit = "res.users"

    is_director = fields.Boolean()
