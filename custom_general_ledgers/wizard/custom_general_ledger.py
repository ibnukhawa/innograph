# -*- coding: utf-8 -*-
import base64
import time
from cStringIO import StringIO

import xlsxwriter
from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class CustomGeneralLedger(models.TransientModel):
    _inherit = "account.report.general.ledger"
    _description = "General Ledger Custom"

    display_account = fields.Selection([('all','All'), ('movement','With movements'), ('without_move','Without movements'),
                                        ('not_zero','With balance is not equal to 0'),], 
                                        string='Display Accounts', required=True, default='movement')
    wbs_ids = fields.Many2many('account.analytic.account', 'account_report_general_ledger_analytic_rel', 'account_analytic_id', 'account_analytic_account', string = 'WBS Code')
    
    def _print_report(self, data):
        data = self.pre_print_report(data)
        data['form'].update(self.read(['initial_balance', 'sortby'])[0])
        if data['form'].get('initial_balance') and not data['form'].get('date_from'):
            raise UserError(_("You must define a Start Date"))
        records = self.env[data['model']].browse(data.get('ids', []))
        return self.env['report'].with_context(landscape=True).get_action(records, 'custom_general_ledgers.report_custom_generalledger', data=data)
    
    
    def check_move_line_month(self, m_y_group, move_lines):
        list_my = []
        if move_lines:
            for l in move_lines:
                list_my.append(l['date_group'])
            if m_y_group in list_my :
                return True
            else:
                return False
        else:
            return False
        
    def get_init_balance(self, move_lines):
        res = []
        for l in move_lines:
            if l['lid'] == 0:
                res.append(l)
                break
            else:
                continue
        return res

    @api.multi
    def print_xls_report(self):
        """Generate XLS Report"""

        # Initialize data
        obj_data = {'ids': self.env.context.get('active_ids', [])}
        obj_data['form'] = self.read(['date_from', 'date_to', 'journal_ids', 'target_move',
                                      'initial_balance', 'sortby', 'display_account', 'wbs_ids'])[0]
        used_context = self._build_contexts(obj_data)
        res = self.read()
        res = res and res[0] or {}
        obj_data.update({'form': res})

        obj_model = self.env['report.custom_general_ledgers.report_custom_generalledger']

        account_ids = obj_data['form'].get('account_ids', False)
        analytic_ids = obj_data['form'].get('wbs_ids', False)
        init_balance = obj_data['form'].get('initial_balance', True)
        sortby = obj_data['form'].get('sortby', 'sort_date')
        display_account = obj_data['form']['display_account']
        docs = self.browse(obj_data)
        codes = []
        
        if obj_data['form'].get('journal_ids', False):
            codes = [journal.code for journal in self.env['account.journal'].search([('id', 'in', obj_data['form']['journal_ids'])])]
        if account_ids:
            accounts = self.env['account.account'].browse(account_ids)
            codes = [account.code for account in accounts]
#         elif self.model == 'account.account':
#             accounts = docs
#             codes = [account.code for account in accounts]
        else:
            accounts = self.env['account.account'].search([])
            codes = [account.code for account in accounts]
            
#         print accounts,'HHHHHHHHHHHH'
        if self.date_from:
            ranges = True
        else:
            ranges = False
        list_my = obj_model.with_context(date_from=self.date_from, strict_range=ranges,
                                             date_to=self.date_to, state=self.target_move, journal_ids=obj_data['form']['journal_ids'],
                                             )._get_list_month_year()
        accounts_id = obj_model.with_context(date_from=self.date_from, strict_range=ranges,
                                             date_to=self.date_to, state=self.target_move, journal_ids=obj_data['form']['journal_ids'],
                                             )._get_account_move_entry_custom(accounts, analytic_ids,
                                                                              init_balance, sortby, display_account)
#         print list_my, '<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<'
        for a in accounts_id:
            if a['move_lines']:
                for l in a['move_lines']:
                    if l['lid'] != 0:
                        l['date_group'] = datetime.strptime(l['ldate'],'%Y-%m-%d').strftime('%B %Y')
                    else:
                        continue

        # Create the Excel report
        report = StringIO()
        workbook = xlsxwriter.Workbook(report)
        filename = 'Report General Ledger.xls'

        worksheet = workbook.add_worksheet('Report General Ledger')
        text_format = workbook.add_format({'text_wrap': True})

        # Set the formatting for report
        doc_header = workbook.add_format({'bold': 1, 'font_size': 16})
        doc_header.set_align('left')

        header = workbook.add_format({'bold': 1, 'align': 'center'})
        header.set_align('vcenter')
        header.set_border()

        cell = workbook.add_format({})
        cell.set_right()
        cell.set_left()

        cell_header = workbook.add_format({'bold': 1})
        cell_header.set_right()
        cell_header.set_left()

        cell_right = workbook.add_format({})
        cell_right.set_num_format('#,##0_);(#,##0)')
        cell_right.set_align('right')
        cell_right.set_right()
        cell_right.set_left()

        cell_center = workbook.add_format({})
        cell_center.set_align('center')
        cell_center.set_right()
        cell_center.set_left()

        footer = workbook.add_format({'bold': 1})
        footer.set_border()

        footer_right = workbook.add_format({'bold': 1})
        footer_right.set_num_format('#,##0_);(#,##0)')
        footer_right.set_align('right')
        footer_right.set_border()

        footer_center = workbook.add_format({'bold': 1})
        footer_center.set_align('center')
        footer_center.set_border()

        white = workbook.add_format({'color': 'white'})

        worksheet.set_row(0, 20)
        worksheet.set_column(0, 0, 32, doc_header)


        worksheet.set_column(1, 12, 16)

        worksheet.merge_range(0, 0, 0, 10, self.company_id.name + ' : ' + 'General Ledger')
        worksheet.write(2, 0, 'Sorted By:', cell_header)
        if self.sortby == 'sort_date':
            worksheet.write(3, 0, 'Date', cell)
        elif self.sortby == 'sort_journal_partner':
            worksheet.write(3, 0, 'Journal & Partner', cell)

        # Set the date
        date_from = ''
        date_to = time.strftime('%d/%m/%y', time.strptime(self.date_to, '%Y-%m-%d'))

        if self.date_from:
            date_from = time.strftime('%d/%m/%y', time.strptime(self.date_from, '%Y-%m-%d'))
            worksheet.write(2, 2, 'Date from :' + date_from, cell_header)
            worksheet.write(3, 2, 'Date to :' + date_to, cell_header)
        else:
             worksheet.write(2, 2, 'Date to :' + date_to, cell_header)

        worksheet.write(2, 4, 'Display Account', cell_header)
        if self.display_account == 'all':
            worksheet.write(3, 4, 'All Account', cell)
        elif self.display_account == 'movement':
            worksheet.write(3, 4, 'With movements', cell)
        elif self.display_account == 'without_move':
            worksheet.write(3, 4, 'Without movements', cell)
        elif self.display_account == 'not_zero':
            worksheet.write(3, 4, 'With balance not equal to zero', cell)

        worksheet.write(2, 6, 'Target Moves:', cell_header)
        if self.target_move == 'all':
            worksheet.write(3, 6, 'All Entries', cell)
        elif self.target_move == 'posted':
            worksheet.write(3, 6, 'All Posted Entries', cell)

        worksheet.write(4, 0, 'Accounts:', cell_header)
        code_acc = ', '.join([ code or '' for code in codes ])
        worksheet.merge_range(5, 0, 5, 8, code_acc, text_format)
        
        worksheet.write(7, 0, 'Date', header)
        worksheet.write(7, 1, 'Partner', header)
        worksheet.write(7, 2, 'Ref', header)
        worksheet.write(7, 3, 'Move', header)
        worksheet.write(7, 4, 'Description', header)
        worksheet.write(7, 5, 'WBS', header)
        worksheet.write(7, 6, 'Debit', header)
        worksheet.write(7, 7, 'Credit', header)
        worksheet.write(7, 8, 'Balance', header)

        tm_opening=0
        tm_opening_debit=0
        tm_opening_credit=0
        tot_mutasi=0
        tot_mutasi_debit=0
        tot_mutasi_credit=0
        tm_grand=0
        tm_grand_debit=0
        tm_grand_credit=0
        row = 8        
        for acc in accounts_id:
            
            worksheet.write(row, 0, acc['code'] + acc['name'], cell_header)
            row += 1
            if self.initial_balance:
                for line in docs.get_init_balance(acc['move_lines']):
                    worksheet.write(row, 4, line['lname'], cell)
                    
                    worksheet.write(row, 6, line['debit'], cell_right)
                    worksheet.write(row, 7, line['credit'], cell_right)
                    worksheet.write(row, 8, line['balance'], cell_right)

                    tm_opening=tm_opening + line['balance']
                    tm_opening_debit=tm_opening_debit + line['debit']
                    tm_opening_credit=tm_opening_credit + line['credit']

                    row += 1
            for list in list_my:
                if docs.check_move_line_month(list, acc['move_lines']) == True:
                    worksheet.write(row, 0, list, cell_header)
                    row += 1

                    tm_debit=0
                    tm_credit=0
                    tm_balance=0
                    for lines in acc['move_lines']:
                        if lines['date_group'] == list and lines['lid'] != 0:
                            tm_debit=tm_debit + lines['debit']
                            tm_credit=tm_credit + lines['credit']
                            tm_balance=tm_balance + lines['balance']
                            date = datetime.strptime(lines['ldate'],'%Y-%m-%d').strftime('%d/%m/%y')
                            worksheet.write(row, 0, date, cell)
                            worksheet.write(row, 1, lines['partner_name'], cell)
                            if lines['lref']:
                                worksheet.write(row, 2, lines['lref'], cell)
                            worksheet.write(row, 3, lines['move_name'], cell)
                            worksheet.write(row, 4, lines['lname'], cell)
                            worksheet.write(row, 5, lines['ancode'], cell)
                            worksheet.write(row, 6, lines['debit'], cell_right)
                            worksheet.write(row, 7, lines['credit'], cell_right)
                            worksheet.write(row, 8, lines['balance'], cell_right)
                            row += 1
                    worksheet.write(row, 0, 'Activity To Date: ' + list, cell_header)
                    worksheet.write(row, 6, tm_debit, cell_right)
                    worksheet.write(row, 7, tm_credit, cell_right)
                    worksheet.write(row, 8, tm_balance, cell_right)
                    tot_mutasi=tot_mutasi + tm_balance
                    tot_mutasi_debit=tot_mutasi_debit + tm_debit
                    tot_mutasi_credit=tot_mutasi_credit + tm_credit
                    row += 1
            worksheet.write(row, 0, 'Ending Balance ' + acc['name'], cell_header)
            worksheet.write(row, 6, acc['debit'], cell_right)
            worksheet.write(row, 7, acc['credit'], cell_right)
            worksheet.write(row, 8, acc['balance'], cell_right)
            tm_grand=tm_grand + acc['balance']
            tm_grand_debit=tm_grand_debit + acc['debit']
            tm_grand_credit=tm_grand_credit + acc['credit']
            row += 1

        worksheet.write(row, 0, 'Total Opening Balance', cell_header)
        worksheet.write(row, 6, tm_opening_debit, cell_right)
        worksheet.write(row, 7, tm_opening_credit, cell_right)
        worksheet.write(row, 8, tm_opening, cell_right)
        row += 1

        worksheet.write(row, 0, 'Total Activity To Date', cell_header)
        worksheet.write(row, 6, tot_mutasi_debit, cell_right)
        worksheet.write(row, 7, tot_mutasi_credit, cell_right)
        worksheet.write(row, 8, tot_mutasi, cell_right)
        row += 1

        worksheet.write(row, 0, 'Total Ending Balance', cell_header)
        worksheet.write(row, 6, tm_grand_debit, cell_right)
        worksheet.write(row, 7, tm_grand_credit, cell_right)
        worksheet.write(row, 8, tm_grand, cell_right)
        row += 1
        # Close the report & show the download form
        workbook.close()
        output = base64.encodestring(report.getvalue())
        report.close()

        view = self.env.ref('custom_general_ledgers.general_ledger_report_xls')
        wizard = self.env['general.ledger.report.xls'].create({
            'report': output,
            'name': filename,
        })

        return {
            'name': _('Download Report'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'general.ledger.report.xls',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': wizard.id,
        }

class GeneralLedgerExcel(models.TransientModel):
    _name = 'general.ledger.report.xls'
    _description = 'General Ledger Report XLS File'

    report = fields.Binary('File', readonly=True)
    name = fields.Char('File Name', readonly=True)
