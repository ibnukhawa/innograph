# -*- coding: utf-8 -*-
"""Inherit HR Holidays Status Module"""
from odoo import models, fields


class HrHolidaysStatus(models.Model):
    """Inherit Model HR Holidays Status"""
    _inherit = "hr.holidays.status"

    category = fields.Selection([('regular', 'Cuti Regular'),
                                 ('sick', 'Cuti Sakit'),
                                 ('reward', 'Cuti Reward'),
                                 ('yearly', 'Cuti Tahunan'),
                                 ('specific', 'Cuti Khusus')],
                                help='- cuti regular : perhitungan masuk ke report cuti biasa\n'
                                     '- cuti sakit : perhitungan masuk ke report cuti sakit\n'
                                     '- cuti reward : perhitungan masuk ke report cuti reward\n'
                                     '- cuti tahunan : perhitungan masuk ke report cuti tahunan\n'
                                     '- cuti khusus : perhitungan masuk ke report cuti biasa\n')
    # TODO : move this field to correct module
    show_deficit = fields.Boolean(help="display real leave deficit of leave usage in website portal")