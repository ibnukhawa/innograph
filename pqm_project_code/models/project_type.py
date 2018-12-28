# -*- coding: utf-8 -*-
""" pqm_project_code"""
from odoo import models, fields, api, _
from odoo import exceptions


class ProjectType(models.Model):
    """ pqm_project_code"""
    _name = "project.type"

    code = fields.Char(size=3)
    name = fields.Char()
    description = fields.Text()
    sequence_id = fields.Many2one(comodel_name='ir.sequence')
    income_account_id = fields.Many2one(
        comodel_name='account.account', string="Income Account")
    salary_account_id = fields.Many2one(
        comodel_name='account.account', string="Salaries Account")
    accrued_expense_id = fields.Many2one(
        comodel_name='account.account', string="Salary Allocation")
    discount_account_id = fields.Many2one(
        comodel_name='account.account', string="Discount Account")
    cost_account_ids = fields.Many2many('account.account', string="Cost of Sales Account")
    overhead_account_id = fields.Many2one(
        comodel_name='account.account', string="Overhead Account")

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
        for line in self:
            name = line.name
            if line.code:
                name = '['+line.code+'] ' + name
            result.append((line.id, name))
        return result

    @api.model
    def create(self, vals):
        # res = super(ProjectType, self).create(vals)
        if not vals.get('sequence_id'):
            vals.update({'sequence_id': self.sudo()._create_sequence(vals).id})
        return super(ProjectType, self).create(vals)

    @api.model
    def _get_sequence_prefix(self, code):
        prefix = code.upper()
        return prefix + '%(y)s@@'

    @api.model
    def _create_sequence(self, vals):
        """ Create new no_gap entry sequence for every new Journal"""
        prefix = self._get_sequence_prefix(vals['code'])
        seq = {
            'name': vals['name'],
            'implementation': 'no_gap',
            'prefix': prefix,
            'padding': 3,
            'number_increment': 1,
            'number_next': 1,
            'use_date_range': True,
        }
        return self.env['ir.sequence'].create(seq)

    @api.multi
    def write(self, vals):
        # res = super(ProjectType, self).write(vals)
        for project in self:
            if ('code' in vals and project.code != vals['code']):
                if self.env['project.project'].search([(
                        'project_type_id', 'in', self.ids)], limit=1):
                    raise exceptions.UserError(
                        _('This project type already contains items, therefore you cannot modify its short name.'))
                new_prefix = self._get_sequence_prefix(vals['code'])
                project.sequence_id.write({'prefix': new_prefix})
            return super(ProjectType, self).write(vals)
