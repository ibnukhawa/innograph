# -*- coding: utf-8 -*-
from odoo import api, fields, models


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    date_scheduled = fields.Datetime('Scheduled Date')
    job_description = fields.Text()

    @api.multi
    @api.depends('move_raw_ids')
    def _has_moves(self):
        super(MrpProduction, self)._has_moves()
        for mo in self:
            mo.has_moves = any([mv.state != 'cancel' for mv in mo.move_raw_ids])

    @api.multi
    def set_draft(self):
        self.write({'state': 'draft'})

    @api.multi
    def action_open_project(self):
        return

    @api.multi
    def action_open_sale(self):
        return
