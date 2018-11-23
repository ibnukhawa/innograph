# -*- coding: utf-8 -*-
from odoo import fields, models, api, _


class EventRegistration(models.Model):
    _inherit = "event.registration"

    nickname = fields.Char('Nick Name')
    function = fields.Char('Job Position')

    @api.model
    def create(self, vals):
        res = super(EventRegistration, self).create(vals)
        if res.contact_id and res.nickname:
            res.contact_id.write({
                'nickname': res.nickname,
                'function': res.function,
            })
        return res