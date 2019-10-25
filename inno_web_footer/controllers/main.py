# -*- coding: utf-8 -*-

from odoo.http import route, request
from odoo.addons.website_mass_mailing.controllers.main import MassMailController


class MassMailControllerCustom(MassMailController):
    @route('/website_mass_mailing/subscribe', type='json', website=True, auth="public")
    def subscribe(self, list_id, email, **post):
        """
        extend base method to customize subscription feature
        """
        mass_mailing_obj = request.env['mail.mass_mailing.list'].sudo()

        if list_id == 0 or not list_id:
            newsletter = mass_mailing_obj.search([('name', 'ilike', 'Newsletter')], limit=1)
            if newsletter:
                list_id = newsletter.id

        res = super(MassMailControllerCustom, self).subscribe(list_id, email, **post)

        return res
