# -*- coding: utf-8 -*-
""" pqm_project_code"""
from odoo import models, fields, api


class ProjectSme(models.Model):
    """ pqm_project_code"""
    _name = "project.sme"

    code = fields.Char(size=2)
    name = fields.Char()
    description = fields.Text()
    sub_sme_ids = fields.One2many(
        string="Sub SME", comodel_name='project.sub.sme', inverse_name="sme_id")

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        """ pqm_project_code"""
        args = args or []
        domain = []
        if name:
            domain = ['|', ('name', operator, name), ('code', operator, name)]
        proj = self.search(domain + args, limit=limit)
        return proj.name_get()

    @api.multi
    @api.depends('name', 'code')
    def name_get(self):
        """ pqm_project_code"""
        result = []
        for sme in self:
            name = sme.name
            if sme.code:
                name = '['+sme.code+'] ' + name
            result.append((sme.id, name))
        return result
