# -*- coding:utf-8 -*-
import logging
from datetime import date, datetime, time

from openerp import SUPERUSER_ID, _, api, fields, models
from openerp.report import report_sxw

# import mount_to_text
# from openerp.addons.amount_to_text_id

_log = logging.getLogger(__name__)

def terbilang(bil):
    angka = ["", "Satu", "Dua", "Tiga", "Empat", "Lima", "Enam", "Tujuh", "Delapan", "Sembilan", "Sepuluh", "Sebelas"]
    Hasil = " "
    n = int(bil)
    if n >= 0 and n <= 11:
        Hasil = Hasil + angka[n]
    elif n < 20:
        Hasil = terbilang(n % 10) + " Belas"
    elif n < 100:
        Hasil = terbilang(n / 10) + " Puluh" + terbilang(n % 10)
    elif n < 200:
        Hasil = " Seratus" + terbilang(n - 100)
    elif n < 1000:
        Hasil = terbilang(n / 100) + " Ratus" + terbilang(n % 100)
    elif n < 2000:
        Hasil = " Seribu" + terbilang(n - 1000)
    elif n < 1000000:
        Hasil = terbilang(n / 1000) + " Ribu" + terbilang(n % 1000)
    elif n < 1000000000:
        Hasil = terbilang(n / 1000000) + " Juta" + terbilang(n % 1000000)
    elif n < 1000000000000:
        Hasil = terbilang(n / 1000000000) + " Milyar" + terbilang(n % 1000000000)
    else:
        Hasil = terbilang(n / 1000000000000) + " Triliyun" + terbilang(n % 1000000000000)
    return Hasil


class CustomKwitansiPdf(models.AbstractModel):
    _name = 'report.custom_kwitansi_report.kwitansi_report_template'
    _template = 'custom_kwitansi_report.kwitansi_report_template'

    @api.multi
    def render_html(self, docids, data=None):
        report_obj = self.env['report']
        # model = self.env.context.get('active_model')
        report = report_obj._get_report_from_name(self._template)
        docs = self.env[report.model].browse(docids)
        docargs = {
            'docs_ids': docids,
            'doc_model': report.model,
            'docs': docs,
            'data': data,
            'terbilang': terbilang,
        }
        return report_obj.render(self._template, docargs)


class CustomKwitansiDuplicatePdf(models.AbstractModel):
    _name = 'report.custom_kwitansi_report.kwitansi_duplicate_template'
    _template = 'custom_kwitansi_report.kwitansi_duplicate_template'

    @api.multi
    def render_html(self, docids, data=None):
        report_obj = self.env['report']
        # model = self.env.context.get('active_model')
        report = report_obj._get_report_from_name(self._template)
        docs = self.env[report.model].browse(docids)
        docargs = {
            'docs_ids': docids,
            'doc_model': report.model,
            'docs': docs,
            'data': data,
            'terbilang': terbilang,
        }
        return report_obj.render(self._template, docargs)
