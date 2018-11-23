# -*- coding: utf-8 -*-

from odoo import api, fields, models


class AccountingReport(models.TransientModel):
    _inherit = "accounting.report"
    
    wbs_ids = fields.Many2many('account.analytic.account','accounting_report_rel','accounting_report_id','analytic_account_id', string='WBS Code')
    hide_detail = fields.Boolean('Hide Details')
    
    @api.multi
    def check_report(self):
        res = super(AccountingReport, self.sudo()).check_report()
        data = {}
        data['form'] = self.read(['hide_detail','wbs_ids','account_report_id', 'date_from_cmp', 'date_to_cmp', 'journal_ids', 'filter_cmp', 'target_move'])[0]
        res['data']['form']['used_context'].update({'wbs_ids': data['form']['wbs_ids'] and self.wbs_ids.ids or False})
        res['data']['form']['comparison_context'].update({'wbs_ids': data['form']['wbs_ids'] and self.wbs_ids.ids or False})
        #insert hide detail to data
        res['data']['form']['comparison_context'].update({'hide_detail': self.hide_detail or False})
        codes = ''
        if self.read(['wbs_ids'],False):
            for journal in self.env['account.analytic.account'].search([('id', 'in', self.read(['wbs_ids'])[0]['wbs_ids'])]):
                if codes:
                    codes = codes+", "+journal.name
                else:
                    codes = journal.name
        res['data']['form'].update({'analytic_account_code':codes})
        
        return res