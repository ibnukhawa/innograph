# -*- coding: utf-8 -*-
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
from odoo.report import report_sxw


class BankStatementReportXlsx(ReportXlsx):

    def generate_xlsx_report(self, workbook, data, objects):
        for obj in objects:
            sheet_name = obj.name
            sheet = workbook.add_worksheet(sheet_name[:31])

            bold = workbook.add_format({'bold': True})
            currency = workbook.add_format({
                'num_format': '"' + obj.currency_id.name + ' "#,##0',
                'align': 'left'
            })

            sheet.set_column('A:A', 15)
            sheet.set_column('B:B', 75)
            sheet.set_column('C:C', 45)
            sheet.set_column('D:D', 25)
            sheet.set_column('E:E', 25)

            sheet.write(0, 0, sheet_name, bold)

            sheet.write(2, 0, 'Journal', bold)
            sheet.write(3, 0, 'Date', bold)
            sheet.write(4, 0, 'Starting Balance', bold)
            sheet.write(5, 0, 'Ending Balance', bold)

            sheet.write(2, 1, obj.journal_id.name)
            sheet.write(3, 1, obj.date)
            sheet.write(4, 1, obj.balance_start, currency)
            sheet.write(5, 1, obj.balance_end, currency)

            sheet.write(7, 0, 'Transactions', bold)

            sheet.write(8, 0, 'Date', bold)
            sheet.write(8, 1, 'Label', bold)
            sheet.write(8, 2, 'Partner', bold)
            sheet.write(8, 3, 'Reference', bold)
            sheet.write(8, 4, 'Amount', bold)

            row = 9

            for line in obj.line_ids:
                sheet.write(row, 0, line.date)
                sheet.write(row, 1, line.name)
                if line.partner_id:
                    sheet.write(row, 2, line.partner_id.name)
                else:
                    sheet.write(row, 2, '')
                if line.ref:
                    sheet.write(row, 3, line.ref)
                else:
                    sheet.write(row, 3, '')
                sheet.write(row, 4, line.amount, currency)
                row += 1

BankStatementReportXlsx('report.bank.statement.xlsx',
                        'account.bank.statement', parser=report_sxw.rml_parse)
