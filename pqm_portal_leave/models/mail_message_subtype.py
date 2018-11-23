# pylint: disable=import-error,protected-access,too-few-public-methods
"""Inherit HR Holidays"""
from odoo import api, models, _


class MailMessageSubtype(models.Model):
    """Custom subtype menu"""
    _inherit = "mail.message.subtype"

    @api.model
    def change_default(self):
        """ Change Default """
        subtype = self.search([('res_model', '=', 'hr.holidays'),('name','=','Approved')])
        if subtype:
            subtype.write({'default':False})
