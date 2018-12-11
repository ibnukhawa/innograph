# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class LineOfBusiness(models.Model):
	_name = "res.partner.lob"

	name = fields.Char()

class ResPartner(models.Model):
	_inherit = "res.partner"

	vendor_specialization = fields.Char(string="Spesialisasi / Kompetensi 1")
	lob_id = fields.Many2one('res.partner.lob', "Line of Business")
	specialization_product = fields.Many2many('product.product', 'product_partner_specialization_rel', 
											  'partner_id', 'product_id', string="Products Specialization")
	no_pkp = fields.Boolean(string="No PKP", default=True,
							help="If set True, must fill field NPWP.\n If set False, must fill field NIK")

