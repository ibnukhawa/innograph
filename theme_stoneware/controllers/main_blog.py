# -*- coding: utf-8 -*-

import datetime
import json
import werkzeug
from odoo import http
from odoo.http import request
from odoo import tools
from odoo.addons.website.models.website import slug, unslug
from odoo.exceptions import UserError
from odoo.osv.orm import browse_record
from odoo.tools.translate import _
from odoo import SUPERUSER_ID
from odoo.tools import html2plaintext


from openerp.addons.website_blog.controllers.main import WebsiteBlog

class WebsiteBlog(WebsiteBlog):

	@http.route(['/blog/get_blog_content'], type='http', auth='public', website=True)
	def get_blog_content_data(self, **post):
		value={}
		if post.get('blog_config_id')!='false':
			collection_data=request.env['blog.configure'].browse(int(post.get('blog_config_id')))
			
			url = request.httprequest.url_root
			url_new = url.replace("http://","")
			url_final =  url_new[:-1]
			
			filter_ids = collection_data.blog_ids.filtered(lambda r: r.access_url.url == url_final)

			blog_ids = filter_ids.sorted(key=lambda x: x.create_date)
			
			value.update({
				'blog_slider':collection_data,
				'blog_ids' : blog_ids
				})
		return request.render("theme_stoneware.blog_slider_content", value)

