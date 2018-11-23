# -*- coding: utf-8 -*-
"""pqm_account_invoice_proforma"""
from odoo import models, fields, api, _

class ProjectType(models.Model):
    """class project_type"""
    _inherit = "project.type"

    accrued_sale_id = fields.Many2one('account.account', string="Accrued Sales")
