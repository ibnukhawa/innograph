# -*- coding: utf-8 -*-
import base64
import time
from cStringIO import StringIO

import xlsxwriter

from odoo import _, api, fields, models
from datetime import datetime, timedelta
from odoo.exceptions import UserError
import calendar
import logging
_log = logging.getLogger(__name__)

class ProjectMargin(models.TransientModel):
    _name = 'project.margin.report'
    _description = 'Project Margin Report'

    date_from = fields.Date()
    date_to = fields.Date()
    enable_compare = fields.Boolean()
    date_from_cmp = fields.Date()
    date_to_cmp = fields.Date()
    hide_details = fields.Boolean(default=True)
    # show_budgets = fields.Boolean(default=True)
    # journal_ids = fields.Many2many('account.journal', string='Journals', required=True)
    # date_from = fields.Date(default=lambda *a: time.strftime('%Y-%m-%d'))

    @api.multi
    def check_report(self, data):
        """
         Get the date and print the report
         @return: return report
        """
        self.ensure_one()
        data = {'ids': self.env.context.get('active_ids', [])}
        res = self.read()
        res = res and res[0] or {}
        data.update({'form': res})

        return self.env['report'].with_context(landscape=True).get_action(self, 'pqm_project_code.action_report_project_margin2', data=data)

    @api.multi
    def print_xls_report(self):
        """Generate XLS Report"""

        # Initialize data
        obj_data = {'ids': self.env.context.get('active_ids', [])}
        res = self.read()
        res = res and res[0] or {}
        obj_data.update({'form': res})

        obj_model = self.env['report.pqm_project_code.action_report_project_margin2']

        # Initialize Value
        total = 0.0
        total_budget = 0.0

        total_income = 0.0
        total_budget_income = 0.0
        total_budget_cost = 0.0

        total_discount = 0.0
        total_budget_discount = 0.0

        total_income_cmp = 0.0
        total_budget_income_cmp = 0.0

        total_discount_cmp = 0.0
        total_budget_discount_cmp = 0.0

        total_cost_head = 0.0
        total_budget_cost_head = 0.0

        total_cost_head_cmp = 0.0
        total_budget_cost_head_cmp = 0.0

        # Create the Excel report
        report = StringIO()
        workbook = xlsxwriter.Workbook(report)
        filename = 'Report Project Margin.xls'

        worksheet = workbook.add_worksheet('Report Project Margin')

        # Set the formatting for report
        doc_header = workbook.add_format({'bold': 1, 'font_size': 18})
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

        if self.enable_compare:
            worksheet.set_column(1, 12, 16)
        else:
            worksheet.set_column(1, 6, 16)

        # Write into Report
        if self.enable_compare:
            worksheet.merge_range(0, 0, 0, 12, 'PROFIT MARGIN REPORT BY SALES TYPE')
        else:
            worksheet.merge_range(0, 0, 0, 6, 'PROFIT MARGIN REPORT BY SALES TYPE')

        worksheet.merge_range(1, 0, 2, 0, 'Description', header)

        # Set the date
        date_from = ''
        date_to = time.strftime('%d %B %Y', time.strptime(self.date_to, '%Y-%m-%d'))


        if self.date_from:
            date_from = time.strftime('%d %B %Y', time.strptime(self.date_from, '%Y-%m-%d'))
            worksheet.merge_range(1, 1, 1, 6, date_from + ' - ' + date_to, header)
        else:
            worksheet.merge_range(1, 1, 1, 6, 'Per ' + date_to, header)

        worksheet.write(2, 1, 'Actual', header)
        worksheet.write(2, 2, '%', header)
        worksheet.write(2, 3, 'Budget', header)
        worksheet.write(2, 4, '%', header)
        worksheet.write(2, 5, 'Variance', header)
        worksheet.write(2, 6, '%', header)

        if self.enable_compare:
            date_from_cmp = ''
            date_to_cmp = time.strftime('%d %B %Y', time.strptime(self.date_to_cmp, '%Y-%m-%d'))
            if self.date_from_cmp:
                date_from_cmp = time.strftime('%d %B %Y', time.strptime(self.date_from_cmp, '%Y-%m-%d'))
                worksheet.merge_range(1, 7, 1, 12, date_from_cmp + ' - ' + date_to_cmp, header)
            else:
                worksheet.merge_range(1, 7, 1, 12, 'Per ' + date_to, header)

            worksheet.write(2, 7, 'Actual', header)
            worksheet.write(2, 8, '%', header)
            worksheet.write(2, 9, 'Budget', header)
            worksheet.write(2, 10, '%', header)
            worksheet.write(2, 11, 'Variance', header)
            worksheet.write(2, 12, '%', header)

        all_type = obj_model.get_project_type(obj_data['form'])

        row = 3

        # Sales
        worksheet.write(row, 0, 'SALES', cell_header)
        worksheet.write(row, 1, '', cell)
        worksheet.write(row, 2, '', cell)
        worksheet.write(row, 3, '', cell)
        worksheet.write(row, 4, '', cell)
        worksheet.write(row, 5, '', cell)
        worksheet.write(row, 6, '', cell)

        if self.enable_compare:
            worksheet.write(row, 7, '', cell)
            worksheet.write(row, 8, '', cell)
            worksheet.write(row, 9, '', cell)
            worksheet.write(row, 10, '', cell)
            worksheet.write(row, 11, '', cell)
            worksheet.write(row, 12, '', cell)

        row += 1

        for project_type in all_type:
            worksheet.write(row, 0, project_type.name, cell)
            worksheet.write(row, 1, obj_model.get_actual_income(project_type.id), cell_right)
            worksheet.write(row, 2, obj_model.get_percentage_income(project_type.id), cell_center)
            worksheet.write(row, 3, obj_model.get_budget_income(project_type.id), cell_right)
            worksheet.write(row, 4, obj_model.get_percentage_budget_income(project_type.id), cell_center)
            worksheet.write(row, 5, obj_model.get_income_variance(project_type.id), cell_right)
            worksheet.write(row, 6, obj_model.get_percentage_variance(project_type.id), cell_center)

            total_income += obj_model.get_actual_income(project_type.id)
            total_budget_income += obj_model.get_budget_income(project_type.id)
            total_income_variance = total_income - total_budget_income

            if self.enable_compare:
                worksheet.write(row, 7, obj_model.get_actual_income_cmp(project_type.id), cell_right)
                worksheet.write(row, 8, obj_model.get_percentage_income_cmp(project_type.id), cell_center)
                worksheet.write(row, 9, obj_model.get_budget_income_cmp(project_type.id), cell_right)
                worksheet.write(row, 10, obj_model.get_percentage_budget_income_cmp(project_type.id), cell_center)
                worksheet.write(row, 11, obj_model.get_income_variance_cmp(project_type.id), cell_right)
                worksheet.write(row, 12, obj_model.get_percentage_variance_cmp(project_type.id), cell_center)

                total_income_cmp += obj_model.get_actual_income_cmp(project_type.id)
                total_budget_income_cmp += obj_model.get_budget_income_cmp(project_type.id)
                total_income_variance_cmp = total_income_cmp - total_budget_income_cmp

            row += 1
            
        for project_type in all_type:
            name = "Discount " + project_type.name
            worksheet.write(row, 0, name, cell)
            worksheet.write(row, 1, obj_model.get_actual_discount(project_type.id), cell_right)
            worksheet.write(row, 2, obj_model.get_percentage_discount(project_type.id), cell_center)
            worksheet.write(row, 3, obj_model.get_budget_discount(project_type.id), cell_right)
            worksheet.write(row, 4, obj_model.get_percentage_budget_discount(project_type.id), cell_center)
            worksheet.write(row, 5, obj_model.get_discount_variance(project_type.id), cell_right)
            worksheet.write(row, 6, obj_model.get_percentage_variance_disk(project_type.id), cell_center)

            total += obj_model.get_actual_discount(project_type.id)
            total_discount = total * -1
            total_budget += obj_model.get_budget_discount(project_type.id)
            total_budget_discount = total_budget * -1
            total_discount_variance = total_discount - total_budget_discount

            if self.enable_compare:
                worksheet.write(row, 7, obj_model.get_actual_discount_cmp(project_type.id), cell_right)
                worksheet.write(row, 8, obj_model.get_percentage_discount_cmp(project_type.id), cell_center)
                worksheet.write(row, 9, obj_model.get_budget_discount_cmp(project_type.id), cell_right)
                worksheet.write(row, 10, obj_model.get_percentage_budget_discount_cmp(project_type.id), cell_center)
                worksheet.write(row, 11, obj_model.get_discount_variance_cmp(project_type.id), cell_right)
                worksheet.write(row, 12, obj_model.get_percentage_variance_cmp_disk(project_type.id), cell_center)

                total_discount_cmp += obj_model.get_actual_discount_cmp(project_type.id) * -1
                total_budget_discount_cmp += obj_model.get_budget_discount_cmp(project_type.id) * -1
                total_discount_variance_cmp = total_discount_cmp - total_budget_discount_cmp

            row += 1

        # Total Sales
        total_income_all = total_income - total_discount
        total_budget_income_all = total_budget_income - total_budget_discount
        total_discount_variance_all = total_income_variance - total_discount_variance
        percent_income = round(total_income_all / total_income_all * 100, 1) if total_income_all > 0 else 0.0
        percent_budget_income = round(total_budget_income_all / total_budget_income_all * 100, 1) if total_budget_income_all > 0 else 0.0
        percent_variance_income = round(total_discount_variance_all / total_budget_income_all * 100, 1) if total_budget_income_all > 0 else 0.0

        worksheet.write(row, 0, 'TOTAL SALES', footer)
        worksheet.write(row, 1, total_income_all, footer_right)
        worksheet.write(row, 2, percent_income, footer_center)
        worksheet.write(row, 3, total_budget_income_all, footer_right)
        worksheet.write(row, 4, percent_budget_income, footer_center)
        worksheet.write(row, 5, total_discount_variance_all, footer_right)
        worksheet.write(row, 6, percent_variance_income, footer_center)

        if self.enable_compare:
            total_income_cmp_all = total_income_cmp - total_discount_cmp
            total_budget_income_cmp_all = total_budget_income_cmp - total_budget_discount_cmp
            total_discount_variance_cmp_all = total_income_variance_cmp - total_discount_variance_cmp
            percent_income_cmp = round(total_income_cmp_all / total_income_cmp_all * 100, 1) if total_income_cmp_all > 0 else 0.0
            percent_budget_income_cmp = round(total_budget_income_cmp_all / total_budget_income_cmp_all * 100, 1) if total_budget_income_cmp_all > 0 else 0.0
            percent_variance_income_cmp = round(total_discount_variance_cmp_all / total_budget_income_cmp_all * 100, 1) if total_budget_income_cmp_all > 0 else 0.0

            worksheet.write(row, 7, total_income_cmp_all, footer_right)
            worksheet.write(row, 8, percent_income_cmp, footer_center)
            worksheet.write(row, 9, total_budget_income_cmp_all, footer_right)
            worksheet.write(row, 10, percent_budget_income_cmp, footer_center)
            worksheet.write(row, 11, total_discount_variance_cmp_all, footer_right)
            worksheet.write(row, 12, percent_variance_income_cmp, footer_center)

        row += 1

        # Cost of Sales
        worksheet.write(row, 0, 'COST OF SALES', cell_header)
        worksheet.write(row, 1, '', cell)
        worksheet.write(row, 2, '', cell)
        worksheet.write(row, 3, '', cell)
        worksheet.write(row, 4, '', cell)
        worksheet.write(row, 5, '', cell)
        worksheet.write(row, 6, '', cell)

        if self.enable_compare:
            worksheet.write(row, 7, '', cell)
            worksheet.write(row, 8, '', cell)
            worksheet.write(row, 9, '', cell)
            worksheet.write(row, 10, '', cell)
            worksheet.write(row, 11, '', cell)
            worksheet.write(row, 12, '', cell)

        row += 1

        for project_type in all_type:
            worksheet.write(row, 0, project_type.name, cell)
            worksheet.write(row, 1, obj_model.get_total_actual_cost(project_type.id), cell_right)
            worksheet.write(row, 2, obj_model.get_percentage_total_cost(project_type.id), cell_center)
            worksheet.write(row, 3, obj_model.get_total_budget_cost(project_type.id), cell_right)
            worksheet.write(row, 4, obj_model.get_percentage_total_budget_cost(project_type.id), cell_center)
            worksheet.write(row, 5, obj_model.get_cost_total_variance(project_type.id), cell_right)
            worksheet.write(row, 6, obj_model.get_percentage_tot_variance_cost(project_type.id), cell_center)

            total_cost_head += obj_model.get_total_actual_cost(project_type.id)
            total_budget_cost_head += obj_model.get_total_budget_cost(project_type.id)
            total_cost_variance = total_cost_head - total_budget_cost_head

            if self.enable_compare:
                worksheet.write(row, 7, obj_model.get_total_actual_cost_cmp(project_type.id), cell_right)
                worksheet.write(row, 8, obj_model.get_percentage_total_cost_cmp(project_type.id), cell_center)
                worksheet.write(row, 9, obj_model.get_total_budget_cost_cmp(project_type.id), cell_right)
                worksheet.write(row, 10, obj_model.get_percentage_total_budget_cost_cmp(project_type.id), cell_center)
                worksheet.write(row, 11, obj_model.get_cost_total_variance_cmp(project_type.id), cell_right)
                worksheet.write(row, 12, obj_model.get_percentage_tot_variance_cost_cmp(project_type.id), cell_center)

                total_cost_head_cmp += obj_model.get_total_actual_cost_cmp(project_type.id)
                total_budget_cost_head_cmp += obj_model.get_total_budget_cost_cmp(project_type.id)
                total_cost_variance_cmp = total_cost_head_cmp - total_budget_cost_head_cmp

            row += 1

            if not self.hide_details:
                for cost in obj_model.get_account_cost(project_type):
                    worksheet.write_rich_string(row, 0, white, '.......', cost.name, cell)
                    worksheet.write(row, 1, obj_model.get_actual_cost(cost.id), cell_right)
                    worksheet.write(row, 2, obj_model.get_percentage_cost(cost.id), cell_center)
                    worksheet.write(row, 3, obj_model.get_budget_cost(cost.id), cell_right)
                    worksheet.write(row, 4, obj_model.get_percentage_budget_cost(cost.id), cell_center)
                    worksheet.write(row, 5, obj_model.get_cost_variance(cost.id), cell_right)
                    worksheet.write(row, 6, obj_model.get_percentage_cost_variance(cost.id), cell_center)

                    if self.enable_compare:
                        worksheet.write(row, 7, obj_model.get_actual_cost_cmp(cost.id), cell_right)
                        worksheet.write(row, 8, obj_model.get_percentage_cost_cmp(cost.id), cell_center)
                        worksheet.write(row, 9, obj_model.get_budget_cost_cmp(cost.id), cell_right)
                        worksheet.write(row, 10, obj_model.get_percentage_budget_cost_cmp(cost.id), cell_center)
                        worksheet.write(row, 11, obj_model.get_cost_variance_cmp(cost.id), cell_right)
                        worksheet.write(row, 12, obj_model.get_percentage_cost_variance_cmp(cost.id), cell_center)

                    row += 1

        # Total Cost of Sales
        percent_cost_head = round(total_cost_head / total_income_all * 100, 1) if total_income_all > 0 else 0.0
        percent_budget_cost_head = round(total_budget_cost_head / total_budget_income_all * 100, 1) if total_budget_income_all > 0 else 0.0
        percent_cost_variance = round((total_cost_head - total_budget_cost_head) / total_budget_cost_head * 100, 1) if total_budget_cost_head > 0 else 0.0

        worksheet.write(row, 0, 'TOTAL COST OF SALES', footer)
        worksheet.write(row, 1, total_cost_head, footer_right)
        worksheet.write(row, 2, percent_cost_head, footer_center)
        worksheet.write(row, 3, total_budget_cost_head, footer_right)
        worksheet.write(row, 4, percent_budget_cost_head, footer_center)
        worksheet.write(row, 5, total_cost_variance, footer_right)
        worksheet.write(row, 6, percent_cost_variance, footer_center)

        if self.enable_compare:
            percent_cost_head_cmp = round(total_cost_head_cmp / total_income_cmp_all * 100, 1) if total_income_cmp_all > 0 else 0.0
            percent_budget_cost_head_cmp = round(total_budget_cost_head_cmp / total_budget_income_cmp_all * 100, 1) if total_budget_income_cmp_all > 0 else 0.0
            percent_cost_variance_cmp = round((total_cost_head_cmp - total_budget_cost_head_cmp) / total_budget_cost_head_cmp * 100, 1) if total_budget_cost_head_cmp > 0 else 0.0

            worksheet.write(row, 7, total_cost_head_cmp, footer_right)
            worksheet.write(row, 8, percent_cost_head_cmp, footer_center)
            worksheet.write(row, 9, total_budget_cost_head_cmp, footer_right)
            worksheet.write(row, 10, percent_budget_cost_head_cmp, footer_center)
            worksheet.write(row, 11, total_cost_variance_cmp, footer_right)
            worksheet.write(row, 12, percent_cost_variance_cmp, footer_center)

        row += 1

        # Gross Operating Income
        gross_income = total_income_all - total_cost_head
        gross_budget = total_budget_income_all - total_budget_cost_head

        percent_gross_income = round((total_income_all - total_cost_head) / total_income_all * 100, 1) if total_income_all > 0 else 0.0
        percent_gross_budget = round(gross_budget / total_budget_income_all * 100, 1) if total_budget_income_all > 0 else 0.0
        percent_gross_variance = round((gross_income - gross_budget) / gross_budget * 100, 1) if gross_budget > 0 else 0.0

        worksheet.write(row, 0, 'GROSS OPERATING INCOME', footer)
        worksheet.write(row, 1, gross_income, footer_right)
        worksheet.write(row, 2, percent_gross_income, footer_center)
        worksheet.write(row, 3, gross_budget, footer_right)
        worksheet.write(row, 4, percent_gross_budget, footer_center)
        worksheet.write(row, 5, total_discount_variance_all - total_cost_variance, footer_right)
        worksheet.write(row, 6, percent_gross_variance, footer_center)

        if self.enable_compare:
            gross_income_cmp = total_income_cmp_all - total_cost_head_cmp
            gross_budget_cmp = total_budget_income_cmp_all - total_budget_cost_head_cmp

            percent_gross_income_cmp = round((total_income_cmp_all - total_cost_head_cmp) / total_income_cmp_all * 100, 1) if total_income_cmp_all > 0 else 0.0
            percent_gross_budget_cmp = round(gross_budget_cmp / total_budget_income_cmp_all * 100, 1) if total_budget_income_cmp_all > 0 else 0.0
            percent_gross_variance_cmp = round((gross_income_cmp - gross_budget_cmp) / gross_budget_cmp * 100, 1) if gross_budget_cmp > 0 else 0.0

            worksheet.write(row, 7, gross_income_cmp, footer_right)
            worksheet.write(row, 8, percent_gross_income_cmp, footer_center)
            worksheet.write(row, 9, gross_budget_cmp, footer_right)
            worksheet.write(row, 10, percent_gross_budget_cmp, footer_center)
            worksheet.write(row, 11, total_discount_variance_cmp_all - total_cost_variance_cmp, footer_right)
            worksheet.write(row, 12, percent_gross_variance_cmp, footer_center)

        row += 1

        # Profit Margin
        worksheet.write(row, 0, 'PROFIT MARGIN', cell_header)
        worksheet.write(row, 1, '', cell)
        worksheet.write(row, 2, '', cell)
        worksheet.write(row, 3, '', cell)
        worksheet.write(row, 4, '', cell)
        worksheet.write(row, 5, '', cell)
        worksheet.write(row, 6, '', cell)

        if self.enable_compare:
            worksheet.write(row, 7, '', cell)
            worksheet.write(row, 8, '', cell)
            worksheet.write(row, 9, '', cell)
            worksheet.write(row, 10, '', cell)
            worksheet.write(row, 11, '', cell)
            worksheet.write(row, 12, '', cell)

        row += 1

        margin_actual = 0.0
        margin_budget = 0.0
        margin_variance = 0.0

        margin_actual_cmp = 0.0
        margin_budget_cmp = 0.0
        margin_variance_cmp = 0.0

        for project_type in all_type:
            worksheet.write(row, 0, project_type.name, cell)
            worksheet.write(row, 1, obj_model.get_margin_actual(project_type.id), cell_right)
            worksheet.write(row, 2, obj_model.get_percentage_margin(project_type.id), cell_center)
            worksheet.write(row, 3, obj_model.get_margin_budget(project_type.id), cell_right)
            worksheet.write(row, 4, obj_model.get_percentage_margin_budget(project_type.id), cell_center)
            worksheet.write(row, 5, obj_model.get_margin_variance(project_type.id), cell_right)
            worksheet.write(row, 6, obj_model.get_percentage_margin_variance(project_type.id), cell_center)

            margin_actual += obj_model.get_margin_actual(project_type.id)
            margin_budget += obj_model.get_margin_budget(project_type.id)
            margin_variance += obj_model.get_margin_variance(project_type.id)

            if self.enable_compare:
                worksheet.write(row, 7, obj_model.get_margin_actual_cmp(project_type.id), cell_right)
                worksheet.write(row, 8, obj_model.get_percentage_margin_cmp(project_type.id), cell_center)
                worksheet.write(row, 9, obj_model.get_margin_budget_cmp(project_type.id), cell_right)
                worksheet.write(row, 10, obj_model.get_percentage_margin_budget_cmp(project_type.id), cell_center)
                worksheet.write(row, 11, obj_model.get_margin_variance_cmp(project_type.id), cell_right)
                worksheet.write(row, 12, obj_model.get_percentage_margin_variance_cmp(project_type.id), cell_center)

                margin_actual_cmp += obj_model.get_margin_actual_cmp(project_type.id)
                margin_budget_cmp += obj_model.get_margin_budget_cmp(project_type.id)
                margin_variance_cmp += obj_model.get_margin_variance_cmp(project_type.id)

            row += 1

        # Total Profit Margin
        percent_actual = round(margin_actual / total_income_all * 100, 1) if total_income_all > 0 else 0.0
        percent_budget = round(margin_budget / total_budget_income_all * 100, 1) if total_budget_income_all > 0 else 0.0
        percent_variance = round(margin_variance / margin_budget * 100, 1) if margin_budget > 0 else 0.0

        worksheet.write(row, 0, 'TOTAL PROFIT MARGIN', footer)
        worksheet.write(row, 1, margin_actual, footer_right)
        worksheet.write(row, 2, percent_actual, footer_center)
        worksheet.write(row, 3, margin_budget, footer_right)
        worksheet.write(row, 4, percent_budget, footer_center)
        worksheet.write(row, 5, margin_variance, footer_right)
        worksheet.write(row, 6, percent_variance, footer_center)

        if self.enable_compare:
            percent_actual_cmp = round(margin_actual_cmp / total_income_cmp_all * 100, 1) if total_income_cmp_all > 0 else 0.0
            percent_budget_cmp = round(margin_budget_cmp / total_budget_income_cmp_all * 100, 1) if total_budget_income_cmp_all > 0 else 0.0
            percent_variance_cmp = round(margin_variance_cmp / margin_budget_cmp * 100, 1) if margin_budget_cmp > 0 else 0.0

            worksheet.write(row, 7, margin_actual_cmp, footer_right)
            worksheet.write(row, 8, percent_actual_cmp, footer_center)
            worksheet.write(row, 9, margin_budget_cmp, footer_right)
            worksheet.write(row, 10, percent_budget_cmp, footer_center)
            worksheet.write(row, 11, margin_variance_cmp, footer_right)
            worksheet.write(row, 12, percent_variance_cmp, footer_center)

        # Close the report & show the download form
        workbook.close()
        output = base64.encodestring(report.getvalue())
        report.close()

        view = self.env.ref('pqm_project_code.project_margin_report_xls')
        wizard = self.env['project.margin.report.xls'].create({
            'report': output,
            'name': filename,
        })

        return {
            'name': _('Download Report'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'project.margin.report.xls',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': wizard.id,
        }


class ReportProjectMargin(models.AbstractModel):
    _name = 'report.pqm_project_code.action_report_project_margin2'

    income = {}
    budget_income = {}
    total_income = 0.0
    total_budget_income = 0.0
    total_budget_cost = 0.0
    actual_cost = {}
    budget_cost = {}

    income_cmp = {}
    budget_income_cmp = {}
    total_income_cmp = 0.0
    total_budget_income_cmp = 0.0
    total_budget_cost_cmp = 0.0
    actual_cost_cmp = {}
    budget_cost_cmp = {}

    filter = ''
    filter_cmp = ''
    filter_budget = ''
    filter_budget_cmp = ''
    enable_cmp = False

    cost_type = {}
    cost_account = {}
    cost_budget_account = {}
    total_cost = 0.0
    total_cost_head = 0.0
    total_budget_cost_head = 0.0

    cost_type_cmp = {}
    cost_account_cmp = {}
    cost_budget_account_cmp = {}
    total_cost_cmp = 0.0
    total_cost_head_cmp = 0.0
    total_budget_cost_head_cmp = 0.0

    def _get_domain_date_for_budget(self,data,mode):
        date_to = False
        date_from = False
        month_count = 0
        date_from_yr = False
        date_to_yr = False
        date_from_mt = False
        date_to_mt = False
        
        if mode:
            date_to = data['date_to_cmp']
            date_from = data['date_from_cmp']
        else:
            date_to = data['date_to']
            date_from = data['date_from']
        
        if not date_from:
            raise UserError(_("This report need to compare budget. Please select date from and make sure its first day of a month"))

        if date_to:
            date_to_dt = datetime.strptime(date_to, "%Y-%m-%d")
            date_to_yr = date_to_dt.year
            date_to_mt = date_to_dt.month
            last_day = calendar.monthrange(date_to_yr,date_to_mt)[1]
        if date_from:
            date_from_dt = datetime.strptime(date_from, "%Y-%m-%d")
            date_from_yr = date_from_dt.year
            date_from_mt = date_from_dt.month
        
        #1. filter should be in the same year
        if date_from_yr!=date_to_yr:
            raise UserError(_("This report need to compare budget. Budget defined on the one year. Please choose filter with same YEAR of date"))
        if date_from_mt > date_to_mt:
            raise UserError(_("Month of date to should be not less than date from"))
        month_count = date_to_mt - date_from_mt + 1
            
        #domain return 1/1/same year to 31/12/same year
        #TODO: make it configurable, for example budget should be set yearly or semester or quarter
        date_budget_from = '%s-%s-%s' % (date_from_yr, date_from_mt, '01')
        date_budget_to = '%s-%s-%s' % (date_to_yr, date_to_mt, last_day)
        domain =" cbl.date_from>= '"+ date_budget_from+"' AND cbl.date_to <= '"+date_budget_to+"'"
        
        return domain

    def get_project_type(self, form):
        cr = self.env.cr
        date_from = form['date_from']
        date_to = form['date_to']
        date_from_cmp = form['date_from_cmp']
        date_to_cmp = form['date_to_cmp']
        self.enable_cmp = form['enable_compare']

        filter_date_from = " AND a.date >= '" + str(date_from)+"'" if date_from else ''
        filter_date_to = " AND a.date <= '" + str(date_to)+"'" if date_to else ''
        self.filter = filter_date_from + filter_date_to

        filter_budget = "cbl.date_to>= '" + str(date_to) + "' AND cbl.date_from <= '" + str(date_to) + "'"
        if date_from:
            filter_budget += " AND cbl.date_to >= '" + str(date_from) + "' AND cbl.date_from <= '" + str(date_from) + "'"
        #self.filter_budget = filter_budget
        self.filter_budget = self._get_domain_date_for_budget(form, False)

        filter_date_from_cmp = " AND a.date >= '" + str(date_from_cmp)+"'" if date_from_cmp else ''
        filter_date_to_cmp = " AND a.date <= '" + str(date_to_cmp)+"'" if date_to_cmp else ''
        self.filter_cmp = filter_date_from_cmp + filter_date_to_cmp

        filter_budget_cmp = "cbl.date_to>= '" + str(date_to_cmp) + "' AND cbl.date_from <= '" + str(date_to_cmp) + "'"
        if date_from_cmp:
            filter_budget_cmp += " AND cbl.date_to >= '" + str(date_from_cmp) + "' AND cbl.date_from <= '" + str(date_from_cmp) + "'"
        self.filter_budget_cmp = ""
        if self.enable_cmp:
            self.filter_budget_cmp = self._get_domain_date_for_budget(form, True)

        self.income = {}
        self.total_income = 0.0
        self.discount = {}
        self.total_discount = 0.0
        self.budget_income = {}
        self.budget_discount = {}
        self.budget_cost = {}
        self.total_budget_income = 0.0
        self.total_budget_discount = 0.0
        self.total_budget_cost = 0.0
        self.actual_cost = {}
        self.cost_type = {}
        self.cost_account = {}
        self.cost_budget_account = {}
        self.total_cost = 0.0
        self.total_cost_head = 0.0
        self.total_budget_cost_head = 0.0

        self.income_cmp = {}
        self.total_income_cmp = 0.0
        self.discount_cmp = {}
        self.total_discount_cmp = 0.0
        self.budget_income_cmp = {}
        self.budget_discount_cmp = {}
        self.budget_cost_cmp = {}
        self.total_budget_income_cmp = 0.0
        self.total_budget_discount_cmp = 0.0
        self.total_budget_cost_cmp = 0.0
        self.actual_cost_cmp = {}
        self.cost_type_cmp = {}
        self.cost_account_cmp = {}
        self.cost_budget_account_cmp = {}
        self.total_cost_cmp = 0.0
        self.total_cost_head_cmp = 0.0
        self.total_budget_cost_head_cmp = 0.0

        project_types = self.env['project.type'].search([('income_account_id', '!=', False)])
        for pt in project_types:
            query_actual = """ select COALESCE(SUM(a.debit),0) - COALESCE(SUM(a.credit), 0) as balance
                        From account_move_line a inner join account_move m
                        on m.id=a.move_id
                        where
                        m.state = %s """ + self.filter + """and account_id = %s """

            cr.execute(query_actual, ('posted', pt.income_account_id.id,))
            income_per_account = abs(self.env.cr.fetchone()[0])
            self.income[pt.id] = income_per_account
            self.total_income += income_per_account

            query_budget = """ Select COALESCE(sum(cbl.planned_amount),0)
                        from crossovered_budget_lines cbl
                        LEFT JOIN account_budget_post abd ON abd.id = cbl.general_budget_id
                        LEFT JOIN account_budget_rel abr ON abr.budget_id = abd.id
                        where """ + self.filter_budget + """ and abr.account_id = %s"""

            cr.execute(query_budget, (pt.income_account_id.id,))
            budget_income_per_account = self.env.cr.fetchone()[0]
            self.budget_income[pt.id] = budget_income_per_account
            self.total_budget_income += budget_income_per_account

            if self.enable_cmp is True:
                query_actual_cmp = """ select COALESCE(SUM(a.debit),0) - COALESCE(SUM(a.credit), 0) as balance
                            From account_move_line a inner join account_move m
                            on m.id=a.move_id
                            where
                            m.state = %s """ + self.filter + """and account_id = %s """

                cr.execute(query_actual_cmp, ('posted', pt.income_account_id.id,))
                income_per_account_cmp = abs(self.env.cr.fetchone()[0])
                self.income_cmp[pt.id] = income_per_account_cmp
                self.total_income_cmp += income_per_account_cmp

                query_budget_cmp = """ Select COALESCE(sum(cbl.planned_amount),0)
                            from crossovered_budget_lines cbl
                            LEFT JOIN account_budget_post abd ON abd.id = cbl.general_budget_id
                            LEFT JOIN account_budget_rel abr ON abr.budget_id = abd.id
                            where """ + self.filter_budget_cmp + """ and abr.account_id = %s"""

                cr.execute(query_budget_cmp, (pt.income_account_id.id,))
                budget_income_per_account_cmp = self.env.cr.fetchone()[0]
                self.budget_income_cmp[pt.id] = budget_income_per_account_cmp
                self.total_budget_income_cmp += budget_income_per_account_cmp
########################################################################################################################
        disc_types = self.env['project.type'].search([('discount_account_id', '!=', False)])
        for pt in disc_types:
            query_actual = """ select COALESCE(SUM(a.debit),0) - COALESCE(SUM(a.credit), 0) as balance
                        From account_move_line a inner join account_move m
                        on m.id=a.move_id
                        where
                        m.state = %s """ + self.filter + """and account_id = %s """

            cr.execute(query_actual, ('posted', pt.discount_account_id.id,))
            discount_per_account = self.env.cr.fetchone()[0]
            self.discount[pt.id] = discount_per_account
            self.total_discount += discount_per_account

            query_budget = """ Select COALESCE(sum(cbl.planned_amount),0)
                        from crossovered_budget_lines cbl
                        LEFT JOIN account_budget_post abd ON abd.id = cbl.general_budget_id
                        LEFT JOIN account_budget_rel abr ON abr.budget_id = abd.id
                        where """ + self.filter_budget + """ and abr.account_id = %s"""

            cr.execute(query_budget, (pt.discount_account_id.id,))
            budget_discount_per_account = self.env.cr.fetchone()[0] * -1
            self.budget_discount[pt.id] = budget_discount_per_account
            self.total_budget_discount += budget_discount_per_account

            if self.enable_cmp is True:
                query_actual_cmp = """ select COALESCE(SUM(a.debit),0) - COALESCE(SUM(a.credit), 0) as balance
                            From account_move_line a inner join account_move m
                            on m.id=a.move_id
                            where
                            m.state = %s """ + self.filter + """and account_id = %s """

                cr.execute(query_actual_cmp, ('posted', pt.discount_account_id.id,))
                discount_per_account_cmp = abs(self.env.cr.fetchone()[0])
                self.discount_cmp[pt.id] = discount_per_account_cmp
                self.total_discount_cmp += discount_per_account_cmp

                query_budget_cmp = """ Select COALESCE(sum(cbl.planned_amount),0)
                            from crossovered_budget_lines cbl
                            LEFT JOIN account_budget_post abd ON abd.id = cbl.general_budget_id
                            LEFT JOIN account_budget_rel abr ON abr.budget_id = abd.id
                            where """ + self.filter_budget_cmp + """ and abr.account_id = %s"""

                cr.execute(query_budget_cmp, (pt.discount_account_id.id,))
                budget_discount_per_account_cmp = self.env.cr.fetchone()[0]*-1
                self.budget_discount_cmp[pt.id] = budget_discount_per_account_cmp
                self.total_budget_discount_cmp += budget_discount_per_account_cmp
        self.total_budget_discount = self.total_budget_discount * -1
        self.total_budget_discount_cmp = self.total_budget_discount_cmp * -1
#############################################################################################################################

        types = self.env['project.type'].search([('income_account_id', '!=', False), ('cost_account_ids', '!=', False)])
        for ca in types:
            query_cost_actual = """ select COALESCE(SUM(a.debit),0) - COALESCE(SUM(a.credit), 0) as balance
                        From account_move_line a inner join account_move m
                        on m.id=a.move_id
                        where
                        m.state = %s """ + self.filter + """and account_id in %s """

            cr.execute(query_cost_actual, ('posted', tuple(ca.cost_account_ids.ids),))
            cost_per_account = self.env.cr.fetchone()[0]
            self.actual_cost[ca.id] = cost_per_account
            self.total_cost_head += cost_per_account

            query_cost_budget = """ Select COALESCE(sum(cbl.planned_amount),0)
                        from crossovered_budget_lines cbl
                        LEFT JOIN account_budget_post abd ON abd.id = cbl.general_budget_id
                        LEFT JOIN account_budget_rel abr ON abr.budget_id = abd.id
                        where """ + self.filter_budget + """ and abr.account_id in %s"""

            cr.execute(query_cost_budget, (tuple(ca.cost_account_ids.ids),))
            budget_cost_per_account = self.env.cr.fetchone()[0]
            self.budget_cost[ca.id] = budget_cost_per_account
            self.total_budget_cost_head += budget_cost_per_account

            if self.enable_cmp is True:
                query_cost_actual_cmp = """ select COALESCE(SUM(a.debit),0) - COALESCE(SUM(a.credit), 0) as balance
                            From account_move_line a inner join account_move m
                            on m.id=a.move_id
                            where
                            m.state = %s """ + self.filter_cmp + """and account_id in %s """

                cr.execute(query_cost_actual_cmp, ('posted', tuple(ca.cost_account_ids.ids),))
                cost_per_account_cmp = self.env.cr.fetchone()[0]
                self.actual_cost_cmp[ca.id] = cost_per_account_cmp
                self.total_cost_head_cmp += cost_per_account_cmp

                query_cost_budget_cmp = """ Select COALESCE(sum(cbl.planned_amount),0)
                            from crossovered_budget_lines cbl
                            LEFT JOIN account_budget_post abd ON abd.id = cbl.general_budget_id
                            LEFT JOIN account_budget_rel abr ON abr.budget_id = abd.id
                            where """ + self.filter_budget_cmp + """ and abr.account_id in %s"""

                cr.execute(query_cost_budget_cmp, (tuple(ca.cost_account_ids.ids),))
                budget_cost_per_account_cmp = self.env.cr.fetchone()[0]
                self.budget_cost_cmp[ca.id] = budget_cost_per_account_cmp
                self.total_budget_cost_head_cmp += budget_cost_per_account_cmp

        return project_types

    def get_account_cost(self, project_type):
        cr = self.env.cr
        for c in project_type.cost_account_ids:
            account_id = c.id
            query_actual = """ select COALESCE(SUM(a.debit),0) - COALESCE(SUM(a.credit), 0) as balance
                        From account_move_line a inner join account_move m
                        on m.id=a.move_id
                        where
                        m.state = %s""" + self.filter + """and account_id = %s """

            cr.execute(query_actual, ('posted', account_id,))
            actual_per_account = self.env.cr.fetchone()[0]
            self.cost_account[c.id] = actual_per_account
            self.total_cost += actual_per_account
            query_budget = """ Select COALESCE(sum(cbl.planned_amount),0)
                        from crossovered_budget_lines cbl
                        LEFT JOIN account_budget_post abd ON abd.id = cbl.general_budget_id
                        LEFT JOIN account_budget_rel abr ON abr.budget_id = abd.id
                        where """ + self.filter_budget + """ and abr.account_id = %s"""

            cr.execute(query_budget, (account_id,))
            budget_per_account = self.env.cr.fetchone()[0]
            self.cost_budget_account[c.id] = budget_per_account
            self.total_budget_cost += budget_per_account

            if self.enable_cmp is True:
                query_actual_cmp = """ select COALESCE(SUM(a.debit),0) - COALESCE(SUM(a.credit), 0) as balance
                            From account_move_line a inner join account_move m
                            on m.id=a.move_id
                            where
                            m.state = %s""" + self.filter_cmp + """and account_id = %s """

                cr.execute(query_actual_cmp, ('posted', account_id,))
                actual_per_account_cmp = self.env.cr.fetchone()[0]
                self.cost_account_cmp[c.id] = actual_per_account_cmp
                self.total_cost_cmp += actual_per_account_cmp

                query_budget_cmp = """ Select COALESCE(sum(cbl.planned_amount),0)
                            from crossovered_budget_lines cbl
                            LEFT JOIN account_budget_post abd ON abd.id = cbl.general_budget_id
                            LEFT JOIN account_budget_rel abr ON abr.budget_id = abd.id
                            where """ + self.filter_budget_cmp + """ and abr.account_id = %s"""

                cr.execute(query_budget_cmp, (account_id,))
                budget_per_account_cmp = self.env.cr.fetchone()[0]
                self.cost_budget_account_cmp[c.id] = budget_per_account_cmp
                self.total_budget_cost_cmp += budget_per_account_cmp

        return project_type.cost_account_ids

    def get_actual_cost(self, account_id):
        return self.cost_account[account_id]

    def get_total_income(self):
        _log.info ("----------------------")
        _log.info (self.total_income)
        _log.info (self.total_discount)
        _log.info (self.total_income - self.total_discount)
        _log.info ("=================")
        return self.total_income - self.total_discount

    def get_total_actual_cost(self, project_type_id):
        return self.actual_cost[project_type_id]

    def get_total_cost(self):
        return self.total_cost_head

    def format_bracket(self, amount):
        if amount < 0:
            return '(%s)' % '{0:,.0f}'.format(abs(amount))
        return '{0:,.0f}'.format(amount)

    def get_tot_budget_cost(self):
        return self.total_budget_cost_head

    def get_percentage_all_variance(self):
        if self.total_budget_cost_head:
            return round((self.total_cost_head - self.total_budget_cost_head) / self.total_budget_cost_head * 100, 1)
        else:
            return 0.0

    def get_actual_income(self, project_type_id):
        return self.income[project_type_id]
    
    def get_actual_discount(self, project_type_id):
        if self.discount[project_type_id] > 0 :
            return self.discount[project_type_id] * -1
        else:
            return self.discount[project_type_id]

    def get_percentage_cost(self, account_id):
        if self.total_income:
            return round(self.get_actual_cost(account_id) / (self.total_income + self.total_discount) * 100, 1)
        else:
            return 0.0

    def get_percentage_total_cost(self, project_type_id):
        income_type = self.get_actual_income(project_type_id)
        if income_type:
            return round(self.get_total_actual_cost(project_type_id) / (income_type + self.get_actual_discount(project_type_id)) * 100, 1)
        else:
            return 0.0

    def get_percentage_all_cost(self):
        if self.get_total_income():
            return round(self.get_total_cost() / self.get_total_income() * 100, 1)
        else:
            return 0.0

    def get_percentage_income(self, project_type_id):
        if self.total_income:
#            return round(self.get_actual_income(project_type_id) / (self.total_income + self.total_discount) * 100, 1)
            return round(self.get_actual_income(project_type_id) / (self.get_total_income()) * 100, 1)
        else:
            return 0.0

    def get_percentage_discount(self, project_type_id):
        if self.total_income:
            return round(self.get_actual_discount(project_type_id) / (self.total_income + self.total_discount) * 100, 1)
        else:
            return 0.0

    def get_total_percentage_income(self):
        if self.total_income:
            return round((self.total_income - self.total_discount) / (self.total_income - self.total_discount) * 100, 1)
        else:
            return 0.0

    def get_total_budget_income(self):
        return self.total_budget_income + self.total_budget_discount

    def get_budget_income(self, project_type_id):
        return self.budget_income[project_type_id]

    def get_budget_discount(self, project_type_id):
        return self.budget_discount[project_type_id]*-1

    def get_total_budget_cost(self, project_type_id):
        return self.budget_cost[project_type_id]

    def get_percentage_all_budget_cost(self):
        if self.get_total_budget_income():
            return round(self.get_tot_budget_cost() / (self.get_total_budget_income()) * 100, 1)
        else:
            return 0.0

    def get_budget_cost(self, account_id):
        return self.cost_budget_account[account_id]

    def get_percentage_budget_income(self, project_type_id):
        if self.total_budget_income:
            return round(self.get_budget_income(project_type_id) / (self.total_budget_income + self.total_budget_discount) * 100, 1)
        else:
            return 0.0

    def get_percentage_budget_discount(self, project_type_id):
        if self.total_budget_income:
            return round(self.get_budget_discount(project_type_id) / (self.total_budget_income + self.total_budget_discount) * 100, 1)
        else:
            return 0.0

    def get_total_percentage_budget_income(self):
        if self.total_budget_income:
            return round((self.total_budget_income - self.total_budget_discount) / (self.total_budget_income - self.total_budget_discount) * 100, 1)
        else:
            return 0.0

    def get_percentage_total_budget_cost(self, project_type_id):
        total_net_income = self.get_budget_income(project_type_id)+self.get_budget_discount(project_type_id)
        if total_net_income>0:
            return round(self.get_total_budget_cost(project_type_id) / total_net_income * 100, 1)
        else:
            return 0.0

    def get_percentage_budget_cost(self, account_id):
        if self.total_budget_income:
            return round(self.get_budget_cost(account_id) / (self.total_budget_income + self.total_budget_discount) * 100, 1)
        else:
            return 0.0

    def get_income_variance(self, project_type_id):
        return self.get_actual_income(project_type_id) - self.get_budget_income(project_type_id)

    def get_discount_variance(self, project_type_id):
        return self.get_actual_discount(project_type_id) - self.get_budget_discount(project_type_id)

    def get_total_income_variance(self):
        return (self.get_total_income()) - (self.get_total_budget_income())

    def get_percentage_variance(self, project_type_id):
        if self.get_budget_income(project_type_id):
            return round(self.get_income_variance(project_type_id) / self.get_budget_income(project_type_id) * 100, 1)
        return 0

    def get_percentage_variance_disk(self, project_type_id):
        if self.get_budget_discount(project_type_id):
            return round(self.get_discount_variance(project_type_id) / self.get_budget_discount(project_type_id) * 100, 1)
        return 0


    def get_total_percentage_variance_income(self):
        if self.total_budget_income:
            return round(self.get_total_income_variance() / (self.total_budget_income - self.total_budget_discount) * 100, 1)
        else:
            return 0.0

    def get_cost_total_variance(self, project_type_id):
        return self.get_total_actual_cost(project_type_id) - self.get_total_budget_cost(project_type_id)

    def get_percentage_tot_variance_cost(self, project_type_id):
        if self.get_total_budget_cost(project_type_id):
            return round(self.get_cost_total_variance(project_type_id) / self.get_total_budget_cost(project_type_id) * 100, 1)
        else:
            return 0.0

    def get_cost_variance(self, account_id):
        return self.get_actual_cost(account_id) - self.get_budget_cost(account_id)

    def get_percentage_cost_variance(self, account_id):
        if self.get_budget_cost(account_id):
            return round(self.get_cost_variance(account_id) / self.get_budget_cost(account_id) * 100, 1)
        else:
            return 0.0

    def get_gross_income(self):
        return self.get_total_income() - self.get_total_cost()

    def get_percentage_gross_income(self):
        if self.get_total_income():
            return round(self.get_gross_income() / self.get_total_income()*100,1)
#        round(((self.total_income + self.total_discount) - self.total_cost_head) / (self.total_income + self.total_discount) * 100, 1)
        else:
            return 0.0

    def get_gross_budget(self):
        return (self.total_budget_income + self.total_budget_discount) - self.get_tot_budget_cost()

    def get_gross_percentage_budget(self):
        if self.total_budget_income:
            return round(self.get_gross_budget() / (self.get_total_budget_income()) * 100,1)
        else:
            return 0.0

    def get_gross_percentage_variance(self):
        if self.get_gross_budget():
            return round((self.get_gross_income() - self.get_gross_budget())/self.get_gross_budget() * 100, 1)
        else:
            return 0.0

    def get_margin_actual(self, project_type_id):
        return self.get_actual_income(project_type_id) + self.get_actual_discount(project_type_id) - self.get_total_actual_cost(project_type_id)

    def get_percentage_margin(self, project_type_id):
        if self.get_actual_income(project_type_id):
            return round(self.get_margin_actual(project_type_id) / self.get_actual_income(project_type_id) * 100, 1)
        else:
            return 0.0

    def get_margin_budget(self, project_type_id):
        return self.get_budget_income(project_type_id) + self.get_budget_discount(project_type_id) - self.get_total_budget_cost(project_type_id)

    def get_percentage_margin_budget(self, project_type_id):
        if self.get_budget_income(project_type_id):
            return round(self.get_margin_budget(project_type_id) / self.get_budget_income(project_type_id) * 100, 1)
        else:
            return 0.0

    def get_margin_variance(self, project_type_id):
        return self.get_margin_actual(project_type_id) - self.get_margin_budget(project_type_id)

    def get_percentage_margin_variance(self, project_type_id):
        if self.get_margin_budget(project_type_id):
            return round(self.get_margin_variance(project_type_id) / self.get_margin_budget(project_type_id) * 100, 1)
        else:
            return 0.0

    # Function to generate comparison data
    def get_actual_cost_cmp(self, account_id):
        return self.cost_account_cmp[account_id]

    def get_total_income_cmp(self):
        return self.total_income_cmp - self.total_discount_cmp

    def get_total_actual_cost_cmp(self, project_type_id):
        return self.actual_cost_cmp[project_type_id]

    def get_total_cost_cmp(self):
        return self.total_cost_head_cmp

    def get_tot_budget_cost_cmp(self):
        return self.total_budget_cost_head_cmp

    def get_percentage_all_variance_cmp(self):
        if self.total_budget_cost_head_cmp:
            return round((self.total_cost_head_cmp - self.total_budget_cost_head_cmp) / self.total_budget_cost_head_cmp * 100, 1)
        else:
            return 0.0

    def get_actual_income_cmp(self, project_type_id):
        return self.income_cmp[project_type_id]

    def get_actual_discount_cmp(self, project_type_id):
        if self.discount_cmp[project_type_id] > 0 :
            return self.discount_cmp[project_type_id] * -1
        else :
            return self.discount_cmp[project_type_id]

    def get_percentage_cost_cmp(self, account_id):
        if self.total_income_cmp:
            return round(self.get_actual_cost_cmp(account_id) / (self.total_income_cmp + self.total_discount_cmp) * 100, 1)
        else:
            return 0.0

    def get_percentage_total_cost_cmp(self, project_type_id):
        income_type_cmp = self.get_actual_income_cmp(project_type_id)
        if income_type_cmp:
            return round(self.get_total_actual_cost_cmp(project_type_id) / (income_type_cmp + self.get_actual_discount_cmp(project_type_id)) * 100, 1)
        else:
            return 0.0

    def get_percentage_all_cost_cmp(self):
        if self.total_income_cmp:
            return round(self.get_total_cost_cmp() / self.get_total_income_cmp() * 100, 1)
        else:
            return 0.0

    def get_percentage_income_cmp(self, project_type_id):
        if self.total_income_cmp:
            return round(self.get_actual_income_cmp(project_type_id) / (self.get_total_income_cmp()) * 100, 1)
        else:
            return 0.0

    def get_percentage_discount_cmp(self, project_type_id):
        if self.total_income_cmp:
            return round(self.get_actual_discount_cmp(project_type_id) / (self.total_income_cmp + self.total_discount_cmp) * 100, 1)
        else:
            return 0.0

    def get_total_percentage_income_cmp(self):
        if self.total_income_cmp:
            return round((self.total_income_cmp - self.total_discount_cmp) / (self.total_income_cmp - self.total_discount_cmp) * 100, 1)
        else:
            return 0.0

    def get_total_budget_income_cmp(self):
        return self.total_budget_income_cmp + self.total_budget_discount_cmp

    def get_budget_income_cmp(self, project_type_id):
        return self.budget_income_cmp[project_type_id]

    def get_budget_discount_cmp(self, project_type_id):
        return self.budget_discount_cmp[project_type_id]*-1

    def get_total_budget_cost_cmp(self, project_type_id):
        return self.budget_cost_cmp[project_type_id]

    def get_percentage_all_budget_cost_cmp(self):
        if self.total_budget_income_cmp:
            return round(self.total_budget_cost_cmp / (self.total_budget_income_cmp + self.total_budget_discount_cmp) * 100, 1)
        else:
            return 0.0

    def get_budget_cost_cmp(self, account_id):
        return self.cost_budget_account_cmp[account_id]

    def get_percentage_budget_income_cmp(self, project_type_id):
        if self.total_budget_income_cmp:
            return round(self.get_budget_income_cmp(project_type_id) / (self.total_budget_income_cmp + self.total_budget_discount_cmp) * 100, 1)
        else:
            return 0.0

    def get_percentage_budget_discount_cmp(self, project_type_id):
        if self.total_budget_income_cmp:
            return round(self.get_budget_discount_cmp(project_type_id) / (self.total_budget_income_cmp + self.total_budget_discount_cmp) * 100, 1)
        else:
            return 0.0


    def get_total_percentage_budget_income_cmp(self):
        if self.total_budget_income_cmp:
            return round((self.total_budget_income_cmp - self.total_budget_discount_cmp) / (self.total_budget_income_cmp - self.total_budget_discount_cmp) * 100, 1)
        else:
            return 0.0

    def get_percentage_total_budget_cost_cmp(self, project_type_id):
        total_net_income_cmp = self.get_budget_income_cmp(project_type_id)+self.get_budget_discount_cmp(project_type_id)
        if total_net_income_cmp>0:
            return round(self.get_total_budget_cost_cmp(project_type_id) / total_net_income_cmp * 100, 1)
        else:
            return 0.0

    def get_percentage_budget_cost_cmp(self, account_id):
        total_budget_income_comp = self.total_budget_income + self.total_budget_discount
        if total_budget_income_comp:
            return round(self.get_budget_cost_cmp(account_id) / (total_budget_income_comp) * 100, 1)
        else:
            return 0.0

    def get_income_variance_cmp(self, project_type_id):
        return self.get_actual_income_cmp(project_type_id) - self.get_budget_income_cmp(project_type_id)

    def get_discount_variance_cmp(self, project_type_id):
        return self.get_actual_discount_cmp(project_type_id) - self.get_budget_discount_cmp(project_type_id)

    def get_total_income_variance_cmp(self):
        return (self.get_total_income_cmp()) - (self.get_total_budget_income_cmp())

    def get_percentage_variance_cmp(self, project_type_id):
        if self.get_budget_income_cmp(project_type_id):
            return round(self.get_income_variance_cmp(project_type_id) / self.get_budget_income_cmp(project_type_id) * 100, 1)
        return 0

    def get_percentage_variance_cmp_disk(self, project_type_id):
        if self.get_budget_discount_cmp(project_type_id):
            return round(self.get_discount_variance_cmp(project_type_id) / self.get_budget_discount_cmp(project_type_id) * 100, 1)
        return 0

    def get_total_percentage_variance_income_cmp(self):
        if self.total_budget_income_cmp:
            return round(self.get_total_income_variance_cmp() / (self.total_budget_income_cmp - self.total_budget_discount_cmp) * 100, 1)
        else:
            return 0.0

    def get_cost_total_variance_cmp(self, project_type_id):
        return self.get_total_actual_cost_cmp(project_type_id) - self.get_total_budget_cost_cmp(project_type_id)

    def get_percentage_tot_variance_cost_cmp(self, project_type_id):
        if self.get_total_budget_cost_cmp(project_type_id):
            return round(self.get_cost_total_variance_cmp(project_type_id) / self.get_total_budget_cost_cmp(project_type_id) * 100, 1)
        else:
            return 0.0

    def get_cost_variance_cmp(self, account_id):
        return self.get_actual_cost_cmp(account_id) - self.get_budget_cost_cmp(account_id)

    def get_percentage_cost_variance_cmp(self, account_id):
        if self.get_budget_cost_cmp(account_id):
            return round(self.get_cost_variance_cmp(account_id) / self.get_budget_cost_cmp(account_id) * 100, 1)
        else:
            return 0.0

    def get_gross_income_cmp(self):
        return (self.get_total_income_cmp()) - self.get_total_cost_cmp()

    def get_percentage_gross_income_cmp(self):
        if self.total_income_cmp:
            return round(self.get_gross_income_cmp() / self.get_total_income_cmp()*100,1)
        else:
            return 0.0

    def get_gross_budget_cmp(self):
        return (self.total_budget_income_cmp + self.total_budget_discount_cmp) - self.get_tot_budget_cost_cmp()

    def get_gross_percentage_budget_cmp(self):
        if self.total_budget_income_cmp:
            return round(self.get_gross_budget_cmp() / (self.get_total_budget_income_cmp()) * 100,1)
        else:
            return 0.0

    def get_gross_percentage_variance_cmp(self):
        if self.get_gross_budget_cmp():
            return round((self.get_gross_income_cmp() - self.get_gross_budget_cmp())/self.get_gross_budget_cmp() * 100, 1)
        else:
            return 0.0

    def get_margin_actual_cmp(self, project_type_id):
        return (self.get_actual_income_cmp(project_type_id) + self.get_actual_discount_cmp(project_type_id)) - self.get_total_actual_cost_cmp(project_type_id)

    def get_percentage_margin_cmp(self, project_type_id):
        if self.get_actual_income_cmp(project_type_id):
            return round(self.get_margin_actual_cmp(project_type_id) / self.get_actual_income_cmp(project_type_id) * 100, 1)
        else:
            return 0.0

    def get_margin_budget_cmp(self, project_type_id):
        return self.get_budget_income_cmp(project_type_id) + self.get_budget_discount_cmp(project_type_id) - self.get_total_budget_cost_cmp(project_type_id)

    def get_percentage_margin_budget_cmp(self, project_type_id):
        if self.get_budget_income_cmp(project_type_id):
            return round(self.get_margin_budget_cmp(project_type_id) / self.get_budget_income_cmp(project_type_id) * 100, 1)
        else:
            return 0.0

    def get_margin_variance_cmp(self, project_type_id):
        return self.get_margin_actual_cmp(project_type_id) - self.get_margin_budget_cmp(project_type_id)

    def get_percentage_margin_variance_cmp(self, project_type_id):
        if self.get_margin_budget_cmp(project_type_id):
            return round(self.get_margin_actual_cmp(project_type_id) / self.get_margin_budget_cmp(project_type_id) * 100, 1)
        else:
            return 0.0

    @api.multi
    def render_html(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        docargs = {
            'doc_ids': docids,
            'doc_model': model,
            'data': data,
            'docs': docs,
            'get_project_type': self.get_project_type,
            'get_actual_income': self.get_actual_income,
            'get_percentage_income': self.get_percentage_income,
            'get_percentage_cost': self.get_percentage_cost,
            'get_percentage_total_cost': self.get_percentage_total_cost,
            'total_income': self.get_total_income,
            'total_percentage_income': self.get_total_percentage_income,
            'total_cost': self.get_total_cost,
            'percentage_all_cost': self.get_percentage_all_cost,
            'tot_budget_cost': self.get_tot_budget_cost,
            'get_budget_income': self.get_budget_income,
            'get_budget_cost': self.get_budget_cost,
            'get_percentage_budget_income': self.get_percentage_budget_income,
            'total_budget_income': self.get_total_budget_income,
            'total_percentage_budget_income': self.get_total_percentage_budget_income,
            'get_income_variance': self.get_income_variance,
            'total_variance': self.get_total_income_variance,
            'get_percentage_variance': self.get_percentage_variance,
            'total_percentage_variance': self.get_total_percentage_variance_income,
            'get_cost_total_variance': self.get_cost_total_variance,
            'get_cost_variance': self.get_cost_variance,
            'get_total_actual_cost': self.get_total_actual_cost,
            'get_account_cost': self.get_account_cost,
            'get_actual_cost': self.get_actual_cost,
            'get_total_budget_cost': self.get_total_budget_cost,
            'gross_income': self.get_gross_income,
            'percentage_gross_income': self.get_percentage_gross_income,
            'get_gross_budget': self.get_gross_budget,
            'get_margin_actual': self.get_margin_actual,
            'get_percentage_margin': self.get_percentage_margin,
            'get_margin_budget': self.get_margin_budget,
            'get_margin_variance': self.get_margin_variance,
            'get_percentage_total_budget_cost': self.get_percentage_total_budget_cost,
            'get_percentage_budget_cost': self.get_percentage_budget_cost,
            'get_percentage_tot_variance_cost': self.get_percentage_tot_variance_cost,
            'get_percentage_cost_variance': self.get_percentage_cost_variance,
            'percentage_all_budget_cost': self.get_percentage_all_budget_cost,
            'percentage_all_variance': self.get_percentage_all_variance,
            'get_gross_percentage_budget': self.get_gross_percentage_budget,
            'get_gross_percentage_variance': self.get_gross_percentage_variance,
            'get_percentage_margin_budget': self.get_percentage_margin_budget,
            'percentage_margin_variance': self.get_percentage_margin_variance,

            'get_actual_discount': self.get_actual_discount,
            'get_percentage_discount': self.get_percentage_discount,
            'get_budget_discount': self.get_budget_discount,
            'get_percentage_budget_discount': self.get_percentage_budget_discount,
            'get_discount_variance': self.get_discount_variance,
            'get_percentage_variance_disk': self.get_percentage_variance_disk,
            'get_actual_discount_cmp': self.get_actual_discount_cmp,
            'get_percentage_discount_cmp': self.get_percentage_discount_cmp,
            'get_budget_discount_cmp': self.get_budget_discount_cmp,
            'get_percentage_budget_discount_cmp': self.get_percentage_budget_discount_cmp,
            'get_discount_variance_cmp': self.get_discount_variance_cmp,
            'get_percentage_variance_cmp_disk': self.get_percentage_variance_cmp_disk,

            'get_actual_income_cmp': self.get_actual_income_cmp,
            'get_percentage_income_cmp': self.get_percentage_income_cmp,
            'get_percentage_cost_cmp': self.get_percentage_cost_cmp,
            'get_percentage_total_cost_cmp': self.get_percentage_total_cost_cmp,
            'total_income_cmp': self.get_total_income_cmp,
            'total_percentage_income_cmp': self.get_total_percentage_income_cmp,
            'total_cost_cmp': self.get_total_cost_cmp,
            'percentage_all_cost_cmp': self.get_percentage_all_cost_cmp,
            'tot_budget_cost_cmp': self.get_tot_budget_cost_cmp,
            'get_budget_income_cmp': self.get_budget_income_cmp,
            'get_budget_cost_cmp': self.get_budget_cost_cmp,
            'get_percentage_budget_income_cmp': self.get_percentage_budget_income_cmp,
            'total_budget_income_cmp': self.get_total_budget_income_cmp,
            'total_percentage_budget_income_cmp': self.get_total_percentage_budget_income_cmp,
            'get_income_variance_cmp': self.get_income_variance_cmp,
            'total_variance_cmp': self.get_total_income_variance_cmp,
            'get_percentage_variance_cmp': self.get_percentage_variance_cmp,
            'total_percentage_variance_cmp': self.get_total_percentage_variance_income_cmp,
            'get_cost_total_variance_cmp': self.get_cost_total_variance_cmp,
            'get_cost_variance_cmp': self.get_cost_variance_cmp,
            'get_total_actual_cost_cmp': self.get_total_actual_cost_cmp,
            'get_actual_cost_cmp': self.get_actual_cost_cmp,
            'get_total_budget_cost_cmp': self.get_total_budget_cost_cmp,
            'gross_income_cmp': self.get_gross_income_cmp,
            'percentage_gross_income_cmp': self.get_percentage_gross_income_cmp,
            'get_gross_budget_cmp': self.get_gross_budget_cmp,
            'get_margin_actual_cmp': self.get_margin_actual_cmp,
            'get_percentage_margin_cmp': self.get_percentage_margin_cmp,
            'get_margin_budget_cmp': self.get_margin_budget_cmp,
            'get_margin_variance_cmp': self.get_margin_variance_cmp,
            'get_percentage_total_budget_cost_cmp': self.get_percentage_total_budget_cost_cmp,
            'get_percentage_budget_cost_cmp': self.get_percentage_budget_cost_cmp,
            'get_percentage_tot_variance_cost_cmp': self.get_percentage_tot_variance_cost_cmp,
            'percentage_all_budget_cost_cmp': self.get_percentage_all_budget_cost_cmp,
            'get_percentage_cost_variance_cmp': self.get_percentage_cost_variance_cmp,
            'percentage_all_variance_cmp': self.get_percentage_all_variance_cmp,
            'get_gross_percentage_budget_cmp': self.get_gross_percentage_budget_cmp,
            'get_gross_percentage_variance_cmp': self.get_gross_percentage_variance_cmp,
            'get_percentage_margin_budget_cmp': self.get_percentage_margin_budget_cmp,
            'percentage_margin_variance_cmp': self.get_percentage_margin_variance_cmp,
            'bracket': self.format_bracket
        }
        return self.env['report'].render('pqm_project_code.action_report_project_margin2', docargs)


class ProjectMarginExcel(models.TransientModel):
    _name = 'project.margin.report.xls'
    _description = 'Project Margin Report XLS File'

    report = fields.Binary('File', readonly=True)
    name = fields.Char('File Name', readonly=True)
