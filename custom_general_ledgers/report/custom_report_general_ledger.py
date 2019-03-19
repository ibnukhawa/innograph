# -*- coding: utf-8 -*-

import time
from datetime import datetime
from odoo import api, models


class CustomReportGeneralLedger(models.AbstractModel):
    _name = 'report.custom_general_ledgers.report_custom_generalledger'
    _template = 'custom_general_ledgers.report_custom_generalledger'

    def _get_list_month_year(self):
        # Get list of month year of account
        list_m_y = []
        where = ''
        date_from = self.env.context.get('date_from')
        date_to = self.env.context.get('date_to')
        if date_from and date_to:
            date_from = "'" + str(self.env.context.get('date_from')) + "'"
            date_to = "'" + str(self.env.context.get('date_to')) + "'"
            where = "WHERE date >= "+ date_from +" AND date <= "+ date_to
        elif date_from and not date_to:
            date_from = "'" + str(self.env.context.get('date_from')) + "'"
            where = "WHERE date >= "+ date_from
        elif date_to and not date_from:
            date_to = "'" + str(self.env.context.get('date_to')) + "'"
            where = "WHERE date <= "+ date_to
        self.env.cr.execute(
            """SELECT DISTINCT date_part('month', date) AS month, date_part('year', date) AS year
            FROM account_move_line
            {where_clause}
            GROUP BY date_part('year', date), date_part('month', date), id
            ORDER BY date_part('year', date), date_part('month', date)
            """.format(where_clause=where)
            )
        for e in self.env.cr.dictfetchall():
            my = str("{:.0f}".format(e['month'])) +"-"+ str("{:.0f}".format(e['year']))
            my_date = datetime.strptime(my, '%m-%Y').strftime('%B %Y')
            list_m_y.append(my_date)
        return list_m_y

    def _get_account_move_entry_custom(self, accounts, analytic_ids, \
        init_balance, sortby, display_account):
        """
        :param:
                accounts: the recordset of accounts
                init_balance: boolean value of initial_balance
                sortby: sorting by date or partner and journal
                display_account: type of account(receivable, payable and both)

        Returns a dictionary of accounts with following key and value {
                'code': account code,
                'name': account name,
                'debit': sum of total debit amount,
                'credit': sum of total credit amount,
                'balance': total balance,
                'amount_currency': sum of amount_currency,
                'move_lines': list of move line
        }
        """
        cr = self.env.cr
        MoveLine = self.env['account.move.line']
        move_lines = dict(map(lambda x: (x, []), accounts.ids))
        # Prepare initial sql query and Get the initial move lines
        if init_balance:
            init_tables, init_where_clause, init_where_params = MoveLine.with_context(date_from=self.env.context.get('date_from'), date_to=False, initial_bal=True)._query_get()
            init_wheres = [""]
            if init_where_clause.strip():
                init_wheres.append(init_where_clause.strip())
            init_filters = " AND ".join(init_wheres)
            filters = init_filters.replace('account_move_line__move_id', 'm').replace('account_move_line', 'l')
            sql = ("""SELECT 0 AS lid, l.account_id AS account_id, '' AS ldate, '' AS lcode,
                        '' AS ancode, '' AS date_group, NULL AS amount_currency, '' AS lref, 'Initial Balance' AS lname,
                        COALESCE(SUM(l.debit),0.0) AS debit, 
                        COALESCE(SUM(l.credit),0.0) AS credit, 
                        COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) as balance, 
                        '' AS lpartner_id,\
                        '' AS move_name, '' AS mmove_id, '' AS currency_code,\
                        NULL AS currency_id,\
                        '' AS invoice_id, '' AS invoice_type, '' AS invoice_number,\
                        '' AS partner_name\
                FROM account_move_line l\
                LEFT JOIN account_move m ON (l.move_id=m.id)\
                LEFT JOIN res_currency c ON (l.currency_id=c.id)\
                LEFT JOIN res_partner p ON (l.partner_id=p.id)\
                LEFT JOIN account_invoice i ON (m.id =i.move_id)\
                LEFT JOIN account_analytic_account an ON (l.analytic_account_id = an.id) \
                JOIN account_journal j ON (l.journal_id=j.id)\
                WHERE l.account_id IN %s """ + filters + ' \
                GROUP BY l.account_id')
            params = (tuple(accounts.ids),) + tuple(init_where_params)
            cr.execute(sql, params)
            for row in cr.dictfetchall():
                move_lines[row.pop('account_id')].append(row)

        sql_sort = 'l.date, l.move_id'
        if sortby == 'sort_journal_partner':
            sql_sort = 'j.code, p.name, l.move_id'

        # Prepare sql query base on selected parameters from wizard
        tables, where_clause, where_params = MoveLine._query_get()
        wheres = [""]
        if where_clause.strip():
            wheres.append(where_clause.strip())
        filters = " AND ".join(wheres)
        filters = filters.replace('account_move_line__move_id', 'm').replace('account_move_line', 'l')
        filter_analytic = " "
        if analytic_ids:
            filter_analytic = " AND l.analytic_account_id IN %s"
            
        # Get move lines base on sql query and Calculate the total balance of move lines
        sql = ('''SELECT l.id AS lid, l.account_id AS account_id, l.date AS ldate, j.code AS lcode,
                    an.code AS ancode, '' AS date_group, l.currency_id, l.amount_currency, l.ref AS lref, l.name AS lname,
                    COALESCE(l.debit,0) AS debit, 
                    COALESCE(l.credit,0) AS credit, 
                    COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) AS balance,\
            m.name AS move_name, c.symbol AS currency_code, p.name AS partner_name\
            FROM account_move_line l\
            JOIN account_move m ON (l.move_id=m.id)\
            LEFT JOIN res_currency c ON (l.currency_id=c.id)\
            LEFT JOIN res_partner p ON (l.partner_id=p.id)\
            LEFT JOIN account_analytic_account an ON (l.analytic_account_id = an.id) \
            JOIN account_journal j ON (l.journal_id=j.id)\
            JOIN account_account acc ON (l.account_id = acc.id) \
            WHERE l.account_id IN %s '''+ filter_analytic + filters + ''' \
            GROUP BY l.id, l.account_id, l.date, j.code,an.code, l.currency_id, l.amount_currency, l.ref, l.name, m.name, c.symbol, p.name \
            ORDER BY ''' + sql_sort)
        if analytic_ids:
            params = (tuple(accounts.ids), tuple(analytic_ids),) + tuple(where_params)
        else:
            params = (tuple(accounts.ids),) + tuple(where_params)
        cr.execute(sql, params)

        for row in cr.dictfetchall():
            balance = 0
            for line in move_lines.get(row['account_id']):
                balance += line['debit'] - line['credit']
            row['balance'] += balance
            move_lines[row.pop('account_id')].append(row)

        # Calculate the debit, credit and balance for Accounts
        account_res = []
        for account in accounts:
            currency = account.currency_id and account.currency_id or account.company_id.currency_id
            res = dict((fn, 0.0) for fn in ['ancode', 'date_group', 'credit', 'debit', 'balance'])
            res['code'] = account.code
            res['name'] = account.name
            res['move_lines'] = move_lines[account.id]
            for line in res.get('move_lines'):
                res['debit'] += line['debit']
                res['credit'] += line['credit']
                res['balance'] = line['balance']
                res['ancode'] = line['ancode'] or ''
                res['date_group'] = line['date_group']
            if display_account == 'all':
                account_res.append(res)
            if display_account == 'movement' and res.get('move_lines'):
                account_res.append(res)
            if display_account == 'without_move' and res.get('move_lines'):
                res['move_lines'] = False
                account_res.append(res)
            if display_account == 'not_zero' and not currency.is_zero(res['balance']):
                account_res.append(res)
        return account_res
#         return 0

    @api.model
    def render_html(self, docids, data=None):
        self.model = 'account.report.general.ledger'
        account_ids = data['form'].get('account_ids', False)
        analytic_ids = data['form'].get('wbs_ids', False)
        docs = self.env[self.model].browse(self.env.context.get('active_ids', []))
        init_balance = data['form'].get('initial_balance', True)
        sortby = data['form'].get('sortby', 'sort_date')
        display_account = data['form']['display_account']
        codes = []

        if data['form'].get('journal_ids', False):
            codes = [journal.code for journal in self.env['account.journal'].search([('id', 'in', data['form']['journal_ids'])])]
        if account_ids:
            accounts = self.env['account.account'].browse(account_ids)
            codes = [account.code for account in accounts]
        elif self.model == 'account.account':
            accounts = docs
            codes = [account.code for account in accounts]
        else:
            accounts = self.env['account.account'].search([])
            codes = [account.code for account in accounts]
        list_m_y = self.with_context(data['form'].get('used_context', {}))._get_list_month_year()
        accounts_res = self.with_context(data['form'].get('used_context', {}))._get_account_move_entry_custom(accounts, analytic_ids, init_balance, sortby, display_account)
        for a in accounts_res:
            if a['move_lines']:
                for l in a['move_lines']:
                    if l['lid'] != 0:
                        l['date_group'] = datetime.strptime(l['ldate'],'%Y-%m-%d').strftime('%B %Y')
                    else:
                        continue

        docargs = {
            'doc_ids': docids,
            'doc_model': self.model,
            'data': data['form'],
            'docs': docs,
            'time': time,
            'list_m_y': list_m_y,
            'Accounts': accounts_res,
            'print_account': codes,}
        
        return self.env['report'].render(self._template, docargs)
