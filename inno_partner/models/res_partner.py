# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class LineOfBusiness(models.Model):
    _name = 'res.partner.lob'

    name = fields.Char()


class ResPartner(models.Model):
    _inherit = 'res.partner'

    WRITEABLE_FIELDS = ['no_pkp', 'nik', 'npwp']

    vendor_specialization = fields.Char(string='Spesialisasi / Kompetensi 1')
    lob_id = fields.Many2one('res.partner.lob', 'Line of Business')
    specialization_product = fields.Many2many('product.product', 'product_partner_specialization_rel',
                                              'partner_id', 'product_id', string='Products Specialization')
    no_pkp = fields.Boolean(string='No PKP', default=True,
                            help='If set True, must fill field NPWP.\n If set False, must fill field NIK')

    @api.model
    def create(self, vals):
        """ Add additional validation during user creation. """
        domain = []

        if vals.get('name'):
            domain.append(('name', '=ilike', vals.get('name')))
        if vals.get('email'):
            domain.append(('email', '=', vals.get('email')))

        existing_user = self.search(domain, limit=1)

        if existing_user and existing_user.id:
            raise ValidationError(
                _('Customer / Vendor dengan nama dan email ini sudah terdaftar. '
                  'Silahkan input nama yang lain.'))

        return super(ResPartner, self).create(vals)


    @api.multi
    def write(self, vals):
        if self.env.user.has_group('hr.group_hr_manager'):
            for key in vals.keys():
                if not (key in self.WRITEABLE_FIELDS or key.startswith('context_')):
                    break
            else:
                self = self.sudo()
        return super(ResPartner, self).write(vals)
