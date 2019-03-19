# -*- coding: utf-8 -*-

import time
from odoo import api, models
from odoo.exceptions import UserError
import logging
_log = logging.getLogger(__name__)
class ReportFinancial(models.AbstractModel):
    _inherit = 'report.account.report_financial'

    def get_account_lines(self, data):
        lines = []
        tot = []
        get_compare = data.get('comparison_context')
        hide_detail = get_compare['hide_detail']
        account_financial = self.env['account.financial.report']
        account_report = account_financial.search([('id', '=', data['account_report_id'][0])])
        child_reports = account_report._get_children_by_order()
        res = self.with_context(data.get('used_context'))._compute_report_balance(child_reports)
        if data['enable_filter']:
            comparison_res = self.with_context(data.get('comparison_context'))._compute_report_balance(child_reports)
            for report_id, value in comparison_res.items():
                res[report_id]['comp_bal'] = value['balance']
                report_acc = res[report_id].get('account')
                if report_acc:
                    for account_id, val in comparison_res[report_id].get('account').items():
                        report_acc[account_id]['comp_bal'] = val['balance']

        for report in child_reports:
            level = bool(report.style_overwrite) and report.style_overwrite or report.level
            vals = {
                'name': report.name,
                'type': 'report',
                'level': level,
                 #used to underline the financial report balances
                'account_type': report.type or False,
            }
            #add Total Value at the end of each hierarki lines\
           # _log.info ("tot di atas %s" % tot)
            if tot:           
                while True:
                    if len(tot)>=1:
                        level_tot = tot[-1].get('level') #level_tot = level sebelumnya
                        if level_tot == level or level_tot > level:
                            flag = tot.pop()
                            if flag['account_type'] != "accounts" or hide_detail is False:
                                lines.append(flag)
                        else:
                            break
                    else:
                        break
            children = False
            children = account_financial.search([('parent_id', '=', report.id)],
                                                order='sequence ASC')
            if len(children) > 0:
                vals['children'] = True
            else:
                vals['children'] = False

            balance = res[report.id]['balance'] * report.sign
            if report.type == 'account_report':
                vals['balance'] = balance
            #add balance if hide detail is True
            if hide_detail and report.type == "accounts":
                vals['balance'] = balance
                #add debit and credit in hide detail
                if data['debit_credit'] and data['enable_filter'] is False:
                    vals['debit'] =  res[report.id]['debit']
                    vals['credit'] = res[report.id]['credit']
                #add comparison in hide detail
                if data['enable_filter']:
                    vals['balance_cmp'] = res[report.id]['comp_bal'] * report.sign
                    vals['variance'] = vals['balance_cmp'] - int(vals['balance'])
                    if vals['balance'] and vals['variance']:
                        vals['percent_variance'] = "%.2f" % (vals['variance']/vals['balance'] * 100)
                    else:
                        vals['percent_variance'] = 100
            lines.append(vals)
            #Save Total Value if hide detail is false
            if (balance) and report.type != 'account_report':
                vals = {
                    'name': 'Total '+report.name,
                    'balance': balance,
                    'type': 'report',
                    'level': level,
                    #used to underline the financial report balances
                    'account_type': report.type or False,
                }
                if data['debit_credit'] and data['enable_filter'] is False:
                    vals['debit'] =  res[report.id]['debit']
                    vals['credit'] = res[report.id]['credit']
                if data['enable_filter']:
                    vals['balance_cmp'] = res[report.id]['comp_bal'] * report.sign
                    vals['variance'] = vals['balance_cmp'] - int(vals['balance'])
                    if vals['balance'] and vals['variance']:
                        vals['percent_variance'] = "%.2f" % (vals['variance']/vals['balance'] * 100)
                    else:
                        vals['percent_variance'] = 100
                tot.append(vals)
            if report.display_detail == 'no_detail':
                #the rest of the loop is used to display the details of
                #the financial report, so it's not needed here.
                continue

            if res[report.id].get('account') and hide_detail is False:
                sub_lines = []
                for account_id, value in res[report.id]['account'].items():
                    #if there are accounts to display, we add them to 
                    #the lines with a level equals to their level in
                    #the COA + 1 (to avoid having them with a too low 
                    #level that would conflicts with the level of data
                    #financial reports for Assets, liabilities...)
                    flag = False
                    account = self.env['account.account'].browse(account_id)
                    vals = {
                        'name': account.code + ' ' + account.name,
                        'balance': value['balance'] * report.sign or 0.0,
                        'type': 'account',
                        'level': report.display_detail == 'detail_with_hierarchy' and 4,
                        'account_type': account.internal_type,
                    }
                    if data['debit_credit'] and data['enable_filter'] == False:
                        vals['debit'] = value['debit']
                        vals['credit'] = value['credit']
                        if not account.company_id.currency_id.is_zero(vals['debit']) or not account.company_id.currency_id.is_zero(vals['credit']):
                            flag = True
                    if not account.company_id.currency_id.is_zero(vals['balance']):
                        flag = True
                    if data['enable_filter']:
                        vals['balance_cmp'] = value['comp_bal'] * report.sign
                        vals['variance'] = vals['balance_cmp'] - int(vals['balance'])
                        if vals['balance'] and vals['variance']:
                            vals['percent_variance'] = "%.2f" % (vals['variance']/vals['balance'] * 100)
                        else:
                            vals['percent_variance'] = 100
                        if not account.company_id.currency_id.is_zero(vals['balance_cmp']):
                            flag = True
                    if flag:
                        sub_lines.append(vals)
                lines += sorted(sub_lines, key=lambda sub_line: sub_line['name'])
        for vals in reversed(tot):
            if vals['account_type'] != "accounts" or hide_detail is False:
                lines.append(vals)
        if account_report.show_root_balance:
            vals = {
                'name': account_report.title_root_balance,
                'type': 'root',
                'balance': res[account_report.id]['balance'] * account_report.sign,

            }
        return lines

    def get_parent(self,data):
        account_financial = self.env['account.financial.report']
        account_report = account_financial.search([('id', '=', data['account_report_id'][0])])
        return account_report
    def get_total_balance(self,data):
        account_financial = self.env['account.financial.report']
        account_report = account_financial.search([('id', '=', data['account_report_id'][0])])
        child_reports = account_report._get_children_by_order()
        res = self.with_context(data.get('used_context'))._compute_report_balance(child_reports)
        return res[account_report.id]['balance'] * account_report.sign
    @api.model
    def render_html(self, docids, data=None):
        if not data.get('form') or not self.env.context.get('active_model') or not self.env.context.get('active_id'):
            raise UserError(_("Form content is missing, this report cannot be printed."))

        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_id'))
        report_lines = self.get_account_lines(data.get('form'))
        report_total = self.get_parent(data.get('form'))
        report_total_balance = self.get_total_balance(data.get('form'))
        docargs = {
            'doc_ids': self.ids,
            'doc_model': self.model,
            'data': data['form'],
            'docs': docs,
            'time': time,
            'get_account_lines': report_lines,
            'get_parent': report_total,
            'get_total_balance': report_total_balance,
        }
        return self.env['report'].render('account.report_financial', docargs)