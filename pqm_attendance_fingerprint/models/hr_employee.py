from odoo import fields, api, models, _


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    finger_id = fields.Char("Fingerprint")
    is_consultant = fields.Boolean("Is Consultant")

    _sql_constraints = [
        ('finger_uniq', 'unique (finger_id)', _("Fingerprints already exists !")),
    ]
