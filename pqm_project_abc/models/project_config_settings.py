# -*- coding: utf-8 -*-
""" pqm_project_abc"""
from odoo import fields, models, api, _


class ProjectConfigSettings(models.TransientModel):
    """ pqm_project_abc"""
    _inherit = "project.config.settings"

    timesheet_journal_id = fields.Many2one('account.journal', string="Timesheet Journal")
    
    @api.multi
    def set_timesheet_journal_id(self):
        """ set_timesheet_journal_id """
        return self.env['ir.values'].sudo().set_default(
            'project.config.settings', 'timesheet_journal_id', self.timesheet_journal_id.id)
