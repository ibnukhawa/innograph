# -*- coding: utf-8 -*-
from odoo import api, fields, models
from datetime import datetime
import base64

# from cStringIO import StringIO
# from datetime import datetime


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'
    _template = 'custom_kwitansi_report.kwitansi_report_template'


    is_kwitansi_printed = fields.Boolean('Kwitansi Printed?', default=False, copy=False)
    kwitansi_number = fields.Char('Nomor Kwitansi', copy=False)
    is_printed = fields.Boolean('Printed', default= False)

    delivery_number = fields.Many2one('stock.picking', compute="_get_picking_id")

    def _get_picking_id(self):
        picking = False
        for line in self.invoice_line_ids:
            for so_line in line.sale_line_ids:
                if any(so_line.order_id.picking_ids):
                    picking_ids = so_line.order_id.picking_ids.sorted('id')
                    picking = picking_ids[0].id
                    break
            break
        self.delivery_number = picking



    @api.multi
    def invoice_print(self):
        ref = super(AccountInvoice, self).invoice_print()
        self.is_printed = True

        # Attach the report in the original Sale Order (if any)
        if self.origin:
            report_obj = self.env['report']
            name = 'INV'+str(self.number) + '.pdf' if self.number else 'Invoice.pdf'
            invoice = report_obj.get_pdf([self.id], 'account.report_invoice')
            sale = self.env['sale.order'].search([('name', '=', self.origin)], limit=1)

            if sale:
                self.env['ir.attachment'].create({
                    'name': name,
                    'type': 'binary',
                    'datas': base64.encodestring(invoice),
                    'datas_fname' : name,
                    'res_model': 'sale.order',
                    'res_id': sale.id,
                    'mimetype': 'application/pdf'
                })
        
        return ref

    @api.multi
    def action_view_sale(self):
        self.ensure_one()
        action = self.env.ref('sale.action_orders')
        form_view_id = self.env.ref('sale.view_order_form').id
        sales = []
        for sale in self.invoice_line_ids:
            for line in sale.sale_line_ids:
                sales.append(line.order_id.id)
        sale_ids = self.env['sale.order'].search([('id', 'in', sales)])
        if sale_ids:
            result = {
                'name': action.name,
                'help': action.help,
                'type': action.type,
                'views': [(form_view_id, 'form')],
                'target': action.target,
                'context': action.context,
                'res_model': action.res_model,
                'res_id': sale_ids[0].id,
            }
        else:
            result = {'type': 'ir.actions.act_window_close'}
        return result

    @api.multi
    def action_view_project_project(self):
        self.ensure_one()
        action = self.env.ref('project.open_view_project_all_config')
        form_view_id = self.env.ref('project.edit_project').id

        analytic = []
        for line in self.invoice_line_ids:
            for project in line.account_analytic_id.project_ids:
                analytic.append(project.id)
        project_ids = self.env['project.project'].search([('id', 'in', analytic)])
        if project_ids:
            result = {
                'name': action.name,
                'help': action.help,
                'type': action.type,
                'views': [(form_view_id, 'form')],
                'target': action.target,
                'context': action.context,
                'res_model': action.res_model,
                'res_id': project_ids[0].id,
            }
        else:
            result = {'type': 'ir.actions.act_window_close'}
        return result

    @api.multi
    def proforma_print(self):
        self.ensure_one()
        return self.env['report'].get_action(self, 'account.report_invoice')

    @api.multi
    def call_duplicate_report(self):
        self.ensure_one()
        return self.env['report'].get_action(self, 'custom_kwitansi_report.account_invoice_report_duplicate_custom')

    @api.multi
    def call_label_report(self):
        self.ensure_one()
        return self.env['report'].get_action(self, 'vit_inv_label.label_report')
    
    @api.multi
    def generate_pdf_kwitansi(self):
        report_obj = self.env['report']
        return report_obj.get_action(self, self._template)

    @api.multi
    def generate_pdf_kwitansi_customer(self):
        report_obj = self.env['report']

        # Save the report as attachment
        name = str(self.kwitansi_number) + '.pdf' if self.kwitansi_number else 'Kwitansi.pdf'
        kwitansi = report_obj.get_pdf([self.id], self._template)

        self.env['ir.attachment'].create({
            'name': name,
            'type': 'binary',
            'datas': base64.encodestring(kwitansi),
            'datas_fname' : name,
            'res_model': 'account.invoice',
            'res_id': self.id,
            'mimetype': 'application/pdf'
        })

        # Attach the report in the original Sale Order (if any)
        if self.origin:
            sale = self.env['sale.order'].search([('name', '=', self.origin)], limit=1)

            self.env['ir.attachment'].create({
                'name': name,
                'type': 'binary',
                'datas': base64.encodestring(kwitansi),
                'datas_fname' : name,
                'res_model': 'sale.order',
                'res_id': sale.id,
                'mimetype': 'application/pdf'
            })

        self.is_kwitansi_printed = True

        return report_obj.get_action(self, self._template)

    @api.multi
    def generate_pdf_kwitansi_duplicate(self):
        report_obj = self.env['report']
        template = 'custom_kwitansi_report.kwitansi_duplicate_template'
        return report_obj.get_action(self, template)

    @api.multi
    def invoice_validate(self):
        """Automatically assign the 'kwitansi_number' when the invoice is validated."""
        res = super(AccountInvoice, self).invoice_validate()

        if not self.kwitansi_number:
            self.kwitansi_number = self.env['ir.sequence'].next_by_code('kwitansi.number')

        return res

    @api.multi
    def action_cancel(self):
        """Reset the 'is_kwitansi_printed' status when the invoice is cancelled."""
        res = super(AccountInvoice, self).action_cancel()
        self.is_printed = False
        self.is_kwitansi_printed = False
        return res

    @api.model
    def terbilang(self, number, english=False):
        number = int(number)
        if not english:
            angka = ["", "Satu", "Dua", "Tiga", "Empat", "Lima", "Enam", "Tujuh", "Delapan", "Sembilan", "Sepuluh", "Sebelas"]
            Hasil = " "
            n = number
            if n >= 0 and n <= 11:
                Hasil = Hasil + angka[n]
            elif n < 20:
                Hasil = self.terbilang(n % 10) + " Belas"
            elif n < 100:
                Hasil = self.terbilang(n / 10) + " Puluh" + self.terbilang(n % 10)
            elif n < 200:
                Hasil = " Seratus" + self.terbilang(n - 100)
            elif n < 1000:
                Hasil = self.terbilang(n / 100) + " Ratus" + self.terbilang(n % 100)
            elif n < 2000:
                Hasil = " Seribu" + self.terbilang(n - 1000)
            elif n < 1000000:
                Hasil = self.terbilang(n / 1000) + " Ribu" + self.terbilang(n % 1000)
            elif n < 1000000000:
                Hasil = self.terbilang(n / 1000000) + " Juta" + self.terbilang(n % 1000000)
            elif n < 1000000000000:
                Hasil = self.terbilang(n / 1000000000) + " Milyar" + self.terbilang(n % 1000000000)
            else:
                Hasil = self.terbilang(n / 1000000000000) + " Triliyun" + self.terbilang(n % 1000000000000)
            return Hasil
        else:
            ones = ("", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine")
            tens = ("", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety")
            teens = ("ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen")
            levels = ("", "thousand", "million", "billion", "trillion", "quadrillion", "quintillion", "sextillion", "septillion", "octillion", "nonillion")
            word = ""
            num = reversed(str(number))
            number = ""
            for x in num:
                number += x
            del num
            if len(number) % 3 == 1: number += "0"
            x = 0
            for digit in number:
                if x % 3 == 0:
                    word = levels[x / 3] + ", " + word
                    n = int(digit)
                elif x % 3 == 1:
                    if digit == "1":
                        num = teens[n]
                    else:
                        num = tens[int(digit)]
                        if n:
                            if num:
                                num += "-" + ones[n]
                            else:
                                num = ones[n]
                    word = num + " " + word
                elif x % 3 == 2:
                    if digit != "0":
                        word = ones[int(digit)] + " hundred " + word
                x += 1
            return word.strip(", ").title()

class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    account_analytic_id = fields.Many2one('account.analytic.account',
                                          string='Project Code')
