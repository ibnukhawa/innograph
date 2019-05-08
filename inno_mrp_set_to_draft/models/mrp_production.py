# -*- coding: utf-8 -*-
from odoo import api, fields, models


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    date_scheduled = fields.Datetime('Scheduled Date')
    job_description = fields.Text()

    @api.multi
    def set_draft(self):
        self.write({'state': 'draft'})

    @api.multi
    def action_open_task(self):
        return

    @api.multi
    def action_open_project(self):
        return

    @api.multi
    def action_open_sale(self):
        return
