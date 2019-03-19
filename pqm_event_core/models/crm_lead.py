# -*- coding:utf-8 -*-
from odoo import models, fields, api, tools
from datetime import datetime

class CRMLead(models.Model):
	_inherit = "crm.lead"

	comment_id = fields.Many2one('event.comment', string="Comment")
