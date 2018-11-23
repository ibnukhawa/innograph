# -*- coding: utf-8 -*-
""" pqm_project_code"""
from odoo import models, fields, api


class ProjectSubSme(models.Model):
    """ pqm_project_code"""
    _name = "project.sub.sme"

    code = fields.Char(size=2)
    name = fields.Char()
    description = fields.Text()
    sme_id = fields.Many2one(string="SME", comodel_name='project.sme')
