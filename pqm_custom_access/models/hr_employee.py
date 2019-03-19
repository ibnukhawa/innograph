# -*- coding: utf-8 -*-
""" pqm_custom_access"""
from odoo import fields, api, models, _
USER_PRIVATE_FIELDS = ['password']

class HrEmployee(models.Model):
    """ pqm_custom_access"""
    _inherit = "hr.employee"

    SELF_READABLE_FIELDS = ['birthday', 'overhead_cost', 'account_id', 'resource_id', 'member_passport',
                            'write_date', 'pin', 'id_expiry_date', 'initial_employment_date', 'work_email',
                            'address_id', 'create_uid', 'mobile_phone', 'color', 'message_last_post',
                            'timesheet_cost', 'work_location', 'barcode', 'write_uid', 'personal_mobile', 'joining_date',
                            'work_phone', ' id', 'notes', 'name_related', 'create_date','resource_id']


    manager_only = fields.Boolean(compute='_compute_access')
    office_only = fields.Boolean(compute='_compute_access')

    @api.multi
    def _compute_access(self):
        for employee in self:
            manager = False
            office = False
            user = self.env['res.users'].browse(self.env.uid)
            if user.has_group('hr.group_hr_manager') or user.id == 1:
                print 'INI LOOOOOH'
                manager = True
            elif user.has_group('hr.group_hr_user') and employee.user_id.id != user.id:
                office = True
            
            employee.manager_only = manager
            employee.office_only = office

    @api.multi
    def read(self, fields=None, load='_classic_read'):
        for key in fields:
            if not (key in self.SELF_READABLE_FIELDS or key.startswith('context_')):
                break
            else:
                # safe fields only, so we read as super-user to bypass access rights
                self = self.sudo()
        result = super(HrEmployee, self).read(fields=fields, load=load)
        return result
