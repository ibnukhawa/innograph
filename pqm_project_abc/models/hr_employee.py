# -*- coding: utf-8 -*-
""" pqm_project_abc"""
from odoo import fields, models, _


class HrEmployee(models.Model):
    """ pqm_project_abc"""
    _inherit = "hr.employee"

    overhead_cost = fields.Float(string="Overhead Cost")
