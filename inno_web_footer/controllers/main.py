# -*- coding: utf-8 -*-

from odoo.http import route, request
from odoo.addons.website_mass_mailing.controllers.main import MassMailController


class MassMailControllerCustom(MassMailController):
    @route('/website_mass_mailing/subscribe', type='json', website=True, auth="public")
    def subscribe(self, list_id, email, **post):
        """
        override base method to customize subscription feature
        """
        mass_mailing_obj = request.env['mail.mass_mailing.list'].sudo()
        Contacts = request.env['mail.mass_mailing.contact'].sudo()
        name, email = Contacts.get_name_email(email)

        if list_id == 0 or not list_id:
            newsletter = mass_mailing_obj.search([('name', 'ilike', 'Newsletter')], limit=1)
            if newsletter:
                list_id = newsletter.id

        contact_ids = Contacts.search([
            ('list_id', '=', int(list_id)),
            ('email', '=', email),
        ], limit=1)
        if not contact_ids:
            # inline add_to_list as we've already called half of it
            Contacts.create({'name': name, 'email': email, 'list_id': int(list_id)})
        elif contact_ids.opt_out:
            contact_ids.opt_out = False
        # add email to session
        request.session['mass_mailing_email'] = email
        return True
