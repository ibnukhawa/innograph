# -*- coding: utf-8 -*-
""" pqm_project_code"""
from odoo import fields, models, api, _
from datetime import datetime
from odoo import exceptions


class ProjectProject(models.Model):
    """ pqm_project_code"""
    _inherit = "project.project"

    project_type_id = fields.Many2one(
        string="Project Type",
        comodel_name='project.type', track_visibility='onchange')
    sme_id = fields.Many2one(string="SME", comodel_name='project.sme',
                             track_visibility='onchange')
    code = fields.Char(string="Project Code")
    description = fields.Text(string="Description")
    sub_sme_id = fields.Many2one(
        string="Sub SME", comodel_name='project.sub.sme',
        track_visibility='onchange')
    user_id = fields.Many2one(
        'res.users', string='Project Manager',
        default=lambda self: self.env.user, track_visibility='onchange')

    @api.model
    def create(self, vals):
        """ pqm_project_code"""
        type_id = vals['project_type_id']
        code_type = self.env['project.type'].search([('id', '=', type_id)])
        sme_id = vals['sme_id']
        code_sme = self.env['project.sme'].search([('id', '=', sme_id)])
        code = ''
        if vals.get('code', False):
            code = vals.get('code')
        else:
            sequence_obj = code_type.sequence_id.next_by_id()
            code = sequence_obj.replace('@@', code_sme.code)
            vals['code'] = code
        project_code = super(ProjectProject, self).create(vals)
        project_code.analytic_account_id.code = code
        project_code.analytic_account_id.project_type_id = type_id
        project_code.analytic_account_id.sme_id = sme_id
        return project_code

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        """ pqm_project_code"""
        args = args or []
        domain = []
        if name:
            domain = ['|', ('name', operator, name), ('code', operator, name)]
        proj = self.search(domain + args, limit=limit)
        return proj.name_get()

    def name_get(self):
        """ pqm_project_code"""
        result = []
        for project in self:
            name = project.name
            if project.code:
                date_start = ''
                date_end = ''
                if project.date_start and project.date:
                    date_start = datetime.strptime(
                        project.date_start, '%Y-%m-%d').strftime('%d/%b/%y')
                    date_end = datetime.strptime(
                        project.date, '%Y-%m-%d').strftime('%d/%b/%y')
                    name = '['+project.code+'] %s %s - %s'%(name, date_start, date_end)
                elif project.date_start :
                    date_start = datetime.strptime(
                        project.date_start, '%Y-%m-%d').strftime('%d/%b/%y')
                    name = '['+project.code + \
                        '] %s %s - %s' % (name, date_start, date_end)
                elif project.date:
                    date_end = datetime.strptime(
                        project.date, '%Y-%m-%d').strftime('%d/%b/%y')
                    name = '['+project.code + \
                        '] %s %s - %s' % (name, date_start, date_end)
                else:
                    name = '['+project.code+'] ' + name
            result.append((project.id, name))
        return result


class AnalyticAccount(models.Model):
    """Inherit Analytic account"""
    _inherit = 'account.analytic.account'

    project_type_id = fields.Many2one(
        string="Project Type",
        comodel_name='project.type')
    sme_id = fields.Many2one(string="SME", comodel_name='project.sme')


    @api.multi
    @api.depends('name')
    def name_get(self):
        """ pqm_project_code"""
        result = []
        for project in self:
            print '++++++++++++++++++'
            name = project.name
            if project.project_ids :
                if project.code:
                    date_start = ''
                    date_end = ''
                    if project.project_ids[0].date_start and project.project_ids[0].date:
                        date_start = datetime.strptime(
                            project.project_ids[0].date_start, '%Y-%m-%d').strftime('%d/%b/%y')
                        date_end = datetime.strptime(
                            project.project_ids[0].date, '%Y-%m-%d').strftime('%d/%b/%y')
                        name = '['+project.code+'] %s %s - %s'%(name, date_start, date_end)
                    elif project.project_ids[0].date_start :
                        date_start = datetime.strptime(
                            project.project_ids[0].date_start, '%Y-%m-%d').strftime('%d/%b/%y')
                        name = '['+project.code + \
                            '] %s %s - %s' % (name, date_start, date_end)
                    elif project.project_ids[0].date:
                        date_end = datetime.strptime(
                            project.project_ids[0].date, '%Y-%m-%d').strftime('%d/%b/%y')
                        name = '['+project.code + \
                            '] %s %s - %s' % (name, date_start, date_end)
                    else:
                        name = '['+project.code+'] ' + name
                else :
                    name = name
            else :
                if project.code:
                    name = '['+project.code+'] ' + name
            result.append((project.id, name))
        return result
    

    @api.multi
    def project_create(self, vals):
        '''
        This function is called at the time of analytic account creation and is used to create a project automatically linked to it if the conditions are meet.
        '''
        self.ensure_one()
        Project = self.env['project.project']
        project = Project.with_context(active_test=False).search([(
            'analytic_account_id', '=', self.id)])
        if not project and self._trigger_project_creation(vals):
            if self.project_type_id and self.sme_id:
                project_values = {
                    'name': vals.get('name'),
                    'analytic_account_id': self.id,
                    'project_type_id': vals.get('project_type_id'),
                    'sme_id': vals.get('sme_id'),
                    'use_tasks': True,
                }
                return Project.create(project_values)
        return False

    