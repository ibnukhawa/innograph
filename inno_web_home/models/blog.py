# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError,ValidationError

import logging
_logger = logging.getLogger(__name__)


import re

class BlogPost(models.Model):
	_inherit = 'blog.post'

	def _background_url_parser(self):
		self.ensure_one()
		groups = re.search(r"url\(([^']*)\)", self.cover_properties)
		if groups:
			return groups.group(1)
		else:
			return '/inno_web_home/static/src/img/no-image-icon-1.png'