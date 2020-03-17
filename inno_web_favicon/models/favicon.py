from odoo import api, fields, models
from odoo.http import request


# class WebsiteMenuUrl(models.Model):
#     _name = 'website.menu.url'

#     favicon = fields.Binary(string="Favicon")

class Website(models.Model):
	_inherit = 'website'

	def getFavicon(self):
		
		url = request.httprequest.url_root
		url_new = url.replace("http://","")
		url_final = url_new[:-1]

		domain=[
			('url','=',url_final)
		]

		menu_url = request.env['website.menu.url'].search(domain)
		images= '/web/image/website.menu.url/'+str(menu_url.id)+'/logo/100x100'
		return images



