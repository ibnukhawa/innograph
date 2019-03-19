# -*- coding: utf-8 -*-
from odoo import api, fields, models
import re


class WebsiteMenu(models.Model):
    _inherit = 'website.menu'

    access_type = fields.Selection([
        ('public', 'Public Access'),
        ('customer', 'Customer Access'),
        ('employee', 'Employee Access')
    ], default='public')

    access_url = fields.Selection([
        ('all', 'All'),
        ('event', 'Event'),
        ('non_event', 'Non Event'),
    ], default='all')

    @api.model
    def display_menu(self, user, url):
        if self.access_url != 'all':
            if self.access_url != self._url_type(url):
                return False
        
        if self.access_type == 'public':
            return True
        elif self.access_type == 'customer':
            if user and user.user_has_groups('base.group_portal'):
                return True
            else:
                return False
        elif self.access_type == 'employee':
            if user and user.user_has_groups('base.group_user') and user.employee_ids:
                return True
            else:
                return False
        else:
            return False

    def _url_type(self, url):
        if re.search('events.pqm.co.id', url, re.IGNORECASE):
            return 'event'
        else:
            return 'non_event'