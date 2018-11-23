# -*- coding: utf-8 -*-
from odoo import fields, models, _


class ResPartner(models.Model):
    _inherit = "res.partner"

    nickname = fields.Char('Call')
    npwp_file = fields.Binary('File NPWP')
    lob = fields.Char('Line Of Business')
    is_event_pic = fields.Boolean('PIC Event')
    is_event_finance = fields.Boolean('PIC Finance')