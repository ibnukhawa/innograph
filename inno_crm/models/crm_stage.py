# -*- coding: utf-8 -*-
""" Import """
from odoo import fields, models


class Stage(models.Model):
    """ Inherit CRM Stage"""
    _inherit = 'crm.stage'

    team_ids = fields.Many2many('crm.team', 'crm_stage_team_rel', 'stage_id', 'team_id',
                                string='Teams', ondelete='set null',
                                help='Specific team that uses this stage. \
                                Other teams will not be able to see or use this stage.')
