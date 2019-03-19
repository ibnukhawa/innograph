# -*- coding: utf-8 -*-
""" project additional view """
from odoo import fields, api, models, _
from datetime import date

class ProjectProject(models.Model):
    """ inherited class project project """
    _inherit = "project.project"

    account_manager_id = fields.Many2one('res.users', string="CRO")
    timesheet_budget = fields.Float(string="Mandays")
    timesheet_budget_uom_id = fields.Many2one('product.uom', string="Satuan")
    timesheet_total = fields.Float("Total Timesheet", compute='_Compute_TotalTimesheet')
    timesheet_balance = fields.Float(compute='_Compute_RemainingTimesheet')
    project_lead_id = fields.Many2one('res.users', string="Project Lead")
    project_link = fields.Char(string="Project Link")
    contract_value = fields.Float(String="Nilai Kontrak")
    total_invoice = fields.Float(string="Total Invoice", compute='_compute_account_invoice')
    project_balance = fields.Float(string="Project Balance", compute="_compute_balance_cost_revenue")
    project_balance_invoice = fields.Float(string="Project Margin (%)", compute="_compute_balance_cost_revenue")
    project_contract_presentation = fields.Float(string="Contract Percentage (%)", compute="_compute_account_invoice")
    invoice_count = fields.Float(compute='_compute_account_invoice')
    invoice_date = fields.Date(string='Last Invoice Date', compute='_compute_account_invoice')
    # account_analytic = fields.Many2one(related='line_ids.general_account_id')


    @api.multi
    def _Compute_TotalTimesheet(self):
        if self.timesheet_budget_uom_id :
            total = 0.0
            uom = self.env.user.company_id.project_time_mode_id
            line = self.env['account.analytic.line'].search([('project_id','=', self.id)])
            for sheet in line:
                total += sheet.unit_amount
            self.timesheet_total = uom._compute_quantity(total, self.timesheet_budget_uom_id)

    @api.one
    def _Compute_RemainingTimesheet(self):
        self.timesheet_balance = self.timesheet_budget - self.timesheet_total

    @api.depends('line_ids.move_id.invoice_id', 'contract_value')
    def _compute_account_invoice(self):
        for project in self:
            # count = False
            # invoice = self.env['account.invoice'].search([('commercial_partner_id', '=', self.partner_id.id)])
            # count = len(invoice)
            # invoice_ids = project.mapped('line_ids.move_id.invoice_id')
            invoice_lines = self.env['account.invoice.line'].search([
                ('account_analytic_id', '=', project.analytic_account_id.id),
                 ('invoice_id.type','in',['out_invoice','out_refund']),
                 ('invoice_id.state','in',['open','paid'])
                ])
            invoice_ids = invoice_lines.mapped('invoice_id')
            sorted_invoice = invoice_ids.sorted('date_invoice')
            project.invoice_count = len(invoice_ids)
            project.invoice_date = sorted_invoice and sorted_invoice[-1].date_invoice or False
            total = 0.0
            for line in invoice_ids:
                total += line.amount_untaxed
            project.total_invoice = total

            if project.contract_value:
                project.project_contract_presentation = project.total_invoice/project.contract_value*100
            else:
                project.project_contract_presentation = 0

    @api.multi
    def _compute_balance_cost_revenue(self):
        for project in self:
            balance = self.env['account.analytic.line'].search([('account_id', '=', project.analytic_account_id.id),
                                                                ('general_account_id','!=',False)])
            total = 0.0
            for line in balance:
                total += line.amount
            project.project_balance = total
            
            if project.total_invoice>0:
                project.project_balance_invoice = project.project_balance/project.total_invoice*100
            else:
                project.project_balance_invoice

    @api.multi
    def button_account_invoice(self):
        invoice_lines = self.env['account.invoice.line'].search(
            [('account_analytic_id', '=', self.analytic_account_id.id),
             ('invoice_id.type','in',['out_invoice','out_refund'])])
        invoice_ids = invoice_lines.mapped('invoice_id').ids

        action = self.env.ref('account.action_invoice_tree1').read()[0]
        if len(invoice_ids) > 1:
            action['domain'] = [('id', 'in', invoice_ids)]
        elif len(invoice_ids) == 1:
            action['views'] = [(self.env.ref('account.invoice_form').id, 'form')]
            action['res_id'] = invoice_ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action        

    @api.multi
    def attachment_tree_views(self):
        self.ensure_one()
        return {
            'res_model': 'project.project',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id' : self.id
        }

    @api.model
    def create(self, vals):
        res = super(ProjectProject, self).create(vals)
        if res.invoiceable_project:
            users = []
#             billing = self.env.ref('account.group_account_invoice')
#             for acc in billing.users:
#                 users.append(acc.partner_id.id)
            
            if res.account_manager_id:
                users.append(res.account_manager_id.partner_id.id)
            if res.project_lead_id:
                users.append(res.project_lead_id.partner_id.id)
            admin = self.env.ref('base.group_system')
            for ad in admin.users:
                if ad.partner_id.id not in users:
                    users.append(ad.partner_id.id)
            for usr in users:
                is_follower = self.env['mail.followers'].search([('res_model', '=', 'project.project'),
                                                                 ('partner_id', '=', usr),
                                                                 ('res_id', '=', res.id)])
                if not is_follower:
                    follow_vals = {'res_model': 'project.project',
                                   'res_id':res.id,
                                   'partner_id': usr}
                    self.env['mail.followers'].create(follow_vals)
            res_user = self.env['res.partner'].browse(users)
            email = self.env.ref('pqm_project_additional_view.project_created_template_mail')
            for partner in res_user:
                email_dict = {'subject': 'New Project has been assigned to you',
                             'email_to': partner.email,
                             'body_html': email.body_html
                             }
                email.write(email_dict)
                email.with_context(follower=partner.name).send_mail(res.id, force_send=True)
        return res

    @api.multi
    def write(self, vals):
        result = super(ProjectProject, self).write(vals)
        if 'active' in vals and not vals['active']:
            for res in self:
                if res.invoiceable_project:
                    follower = self.env['mail.followers'].search([('res_model', '=', 'project.project'),
                                                                         ('res_id', '=', res.id)])
                    for usr in follower:
                        analytic_account = self.analytic_account_id
                        analytic_account.active = False
                        res_user = self.env['res.partner'].browse(usr.partner_id.id)
                        email = self.env.ref('pqm_project_additional_view.project_archived_template_mail')
                        for partner in res_user:
                            email_dict = {'subject': 'Project Archived',
                                          'email_to': partner.email,
                                          'body_html': email.body_html
                                          }
                            email.write(email_dict)
                            email.with_context(follower=partner.name).send_mail(res.id, force_send=True)
        return result
