# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#    See LICENSE file for full copyright and licensing details.
#################################################################################
from odoo import api, fields, models, _

class MegaMenuConfig(models.TransientModel):

	_inherit = 'webkul.website.addons'
	_name = 'mega.menu.config'

	display_text_header = fields.Boolean(
		string="Show Mega Menu Header"
	)

	mega_menu_header_text = fields.Char(
		string="Header Text",
		help="Text to be displayed on the Mega menu header"
	)
	mega_menu_header_color = fields.Char(
		string="Header Text Color",
		help="Background color to be displayed on the Mega menu header"
	)
	mega_menu_header_bg = fields.Char(
		string="Header Background Color",
		help="Text color to be displayed on the Mega menu header"
	)
	mega_menu_body_bg = fields.Char(
		string="Body Background Color",
		help="Background color to be displayed on the Mega menu body"
	)
	mega_menu_body_color = fields.Char(
		string="Body Text Color",
		help="Text color to be displayed on the Mega menu body"
	)
	root_categ_color = fields.Char(
		string="Root Category Text Color",
		help="Text color to be displayed on the Mega menu root category"
	)
	mega_menu_type = fields.Selection(
		selection=[('default','Dropdown'),('fly_out','Fly Out')],
		string="Menu Type",
		default='default'
	)
	@api.model
	def get_default_website_votes(self, fields):
		ir_values = self.env['ir.values'].sudo()
		res = {}
		res.update({
			'display_text_header':ir_values.get_default('mega.menu.config','display_text_header'),
			'mega_menu_header_text':ir_values.get_default('mega.menu.config', 'mega_menu_header_text'),
			'mega_menu_header_color':ir_values.get_default('mega.menu.config', 'mega_menu_header_color'),
			'mega_menu_header_bg':ir_values.get_default('mega.menu.config', 'mega_menu_header_bg'),
			'mega_menu_body_bg':ir_values.get_default('mega.menu.config', 'mega_menu_body_bg'),
			'mega_menu_body_color':ir_values.get_default('mega.menu.config', 'mega_menu_body_color'),
			'root_categ_color':ir_values.get_default('mega.menu.config', 'root_categ_color'),
			'mega_menu_type':ir_values.get_default('mega.menu.config', 'mega_menu_type'),
		})
		return res


	@api.multi
	def set_default_website_votes(self):
		ir_values = self.env['ir.values'].sudo()
		ir_values.set_default('mega.menu.config', 'display_text_header', self.display_text_header)
		ir_values.set_default('mega.menu.config', 'mega_menu_header_text', self.mega_menu_header_text)
		ir_values.set_default('mega.menu.config', 'mega_menu_header_color', self.mega_menu_header_color)
		ir_values.set_default('mega.menu.config', 'mega_menu_header_bg', self.mega_menu_header_bg)
		ir_values.set_default('mega.menu.config', 'mega_menu_body_bg', self.mega_menu_body_bg)
		ir_values.set_default('mega.menu.config', 'mega_menu_body_color', self.mega_menu_body_color)
		ir_values.set_default('mega.menu.config', 'root_categ_color', self.root_categ_color)
		ir_values.set_default('mega.menu.config', 'mega_menu_type', self.mega_menu_type)
		return True

