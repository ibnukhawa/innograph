# -*- coding:utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.fields import Date

from odoo.addons.website_portal.controllers.main import website_account
from odoo.addons.website_project_issue.controllers.main import WebsiteAccount

class website_account(website_account):
    @http.route()
    def account(self, **kw):
        values = self._prepare_portal_layout_values()
        user = request.env.user
        partner = request.env.user.partner_id

        SaleOrder = request.env['sale.order']
        Invoice = request.env['account.invoice']
        quotation_count = SaleOrder.sudo().search_count([
            '&', ('state', 'in', ['sent', 'cancel']),
            '|', ('create_uid', '=', user.id),
            ('partner_id', 'child_of', partner.commercial_partner_id.id)
        ])
        order_count = SaleOrder.sudo().search_count([
            '&', ('state', 'in', ['sale', 'done']),
            '|', ('create_uid', '=', user.id),
            ('partner_id', 'child_of', partner.commercial_partner_id.id)
        ])
        invoice_count = Invoice.sudo().search_count([
            '&', ('type', 'in', ['out_invoice', 'out_refund']), '&',
            ('state', 'in', ['open', 'paid', 'cancel']),
            '|', ('create_uid', '=', user.id),
            ('partner_id', 'child_of', partner.commercial_partner_id.id),
        ])

        values.update({
            'quotation_count': quotation_count,
            'order_count': order_count,
            'invoice_count': invoice_count,
        })
        return request.render("website_portal.portal_my_home", values)

    @http.route(['/my/quotes', '/my/quotes/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_quotes(self, page=1, date_begin=None, date_end=None, **kw):
        values = self._prepare_portal_layout_values()
        user = request.env.user
        partner = user.partner_id
        SaleOrder = request.env['sale.order']

        domain = [
            '&', ('state', 'in', ['sent', 'cancel']),
            '|', ('create_uid', '=', user.id), ('partner_id', 'child_of', partner.commercial_partner_id.id)

        ]

        archive_groups = self._get_archive_groups('sale.order', domain)
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # count for pager
        quotation_count = SaleOrder.sudo().search_count(domain)
        # make pager
        pager = request.website.pager(
            url="/my/quotes",
            url_args={'date_begin': date_begin, 'date_end': date_end},
            total=quotation_count,
            page=page,
            step=self._items_per_page
        )
        # search the count to display, according to the pager data
        quotations = SaleOrder.sudo().search(domain, limit=self._items_per_page, offset=pager['offset'])

        values.update({
            'date': date_begin,
            'quotations': quotations,
            'pager': pager,
            'archive_groups': archive_groups,
            'default_url': '/my/quotes',
        })
        return request.render("website_portal_sale.portal_my_quotations", values)

    @http.route(['/my/orders', '/my/orders/page/<int:page>'], type='http', auth="user",website=True)
    def portal_my_orders(self, page=1, date_begin=None, date_end=None, **kw):
        values = self._prepare_portal_layout_values()
        user = request.env.user
        partner = user.partner_id
        SaleOrder = request.env['sale.order']

        domain = [
            '&', ('state', 'in', ['sale', 'done']),
            '|', ('create_uid', '=', user.id), ('partner_id', 'child_of', partner.commercial_partner_id.id)
        ]
        archive_groups = self._get_archive_groups('sale.order', domain)
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # count for pager
        order_count = SaleOrder.sudo().search_count(domain)
        # pager
        pager = request.website.pager(
            url="/my/orders",
            url_args={'date_begin': date_begin, 'date_end': date_end},
            total=order_count,
            page=page,
            step=self._items_per_page
        )
        # content according to pager and archive selected
        orders = SaleOrder.sudo().search(domain, limit=self._items_per_page, offset=pager['offset'])

        values.update({
            'date': date_begin,
            'orders': orders,
            'page_name': 'order',
            'pager': pager,
            'archive_groups': archive_groups,
            'default_url': '/my/orders',
        })
        return request.render("website_portal_sale.portal_my_orders", values)

    @http.route(['/my/invoices', '/my/invoices/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_invoices(self, page=1, date_begin=None, date_end=None, **kw):
        values = self._prepare_portal_layout_values()
        user = request.env.user
        partner = user.partner_id
        AccountInvoice = request.env['account.invoice']

        domain = [
            '&', ('type', 'in', ['out_invoice', 'out_refund']), '&', ('state', 'in', ['open', 'paid', 'cancel']),
            '|', ('create_uid', '=', user.id), ('partner_id', 'child_of', partner.commercial_partner_id.id),
        ]
        archive_groups = self._get_archive_groups('account.invoice', domain)
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # count for pager
        invoice_count = AccountInvoice.sudo().search_count(domain)
        # pager
        pager = request.website.pager(
            url="/my/invoices",
            url_args={'date_begin': date_begin, 'date_end': date_end},
            total=invoice_count,
            page=page,
            step=self._items_per_page
        )
        # content according to pager and archive selected
        invoices = AccountInvoice.sudo().search(domain, limit=self._items_per_page, offset=pager['offset'])
        values.update({
            'date': date_begin,
            'invoices': invoices,
            'page_name': 'invoice',
            'pager': pager,
            'archive_groups': archive_groups,
            'default_url': '/my/invoices',
        })
        return request.render("website_portal_sale.portal_my_invoices", values)

    def _get_archive_groups(self, model, domain=None, fields=None, groupby="create_date", order="create_date desc"):
        if not model:
            return []
        if domain is None:
            domain = []
        if fields is None:
            fields = ['name', 'create_date']
        groups = []
        for group in request.env[model].sudo()._read_group_raw(domain, fields=fields, groupby=groupby, orderby=order):
            dates, label = group[groupby]
            date_begin, date_end = dates.split('/')
            groups.append({
                'date_begin': Date.to_string(Date.from_string(date_begin)),
                'date_end': Date.to_string(Date.from_string(date_end)),
                'name': label,
                'item_count': group[groupby + '_count']
            })
        return groups

class WebsiteAccount(WebsiteAccount):

    def _prepare_portal_layout_values(self):
        """ prepare the values to render portal layout """
        partner = request.env.user.partner_id
        # get customer sales rep
        if partner.user_id:
            sales_rep = partner.user_id
        else:
            sales_rep = False
        values = {
            'sales_rep': sales_rep,
            'company': request.website.company_id,
            'user': request.env.user
        }
        # domain is needed to hide non portal project for employee
        # portal users can't see the privacy_visibility, fetch the domain for them in sudo
        portal_projects = request.env['project.project'].sudo().search([('privacy_visibility', '=', 'portal')])
        issue_count = request.env['project.issue'].sudo().search_count([('project_id', 'in', portal_projects.ids)])
        values.update({
            'issue_count': issue_count,
        })
        return values