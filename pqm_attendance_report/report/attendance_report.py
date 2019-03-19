# -*- coding:utf-8 -*-
import logging
from odoo import SUPERUSER_ID, _, api, fields, models

# import mount_to_text
# from openerp.addons.amount_to_text_id

_log = logging.getLogger(__name__)

class CustomKwitansiPdf(models.AbstractModel):
    _name = 'report.pqm_attendance_report.attendance_report_template'
    _template = 'pqm_attendance_report.attendance_report_template'

    @api.multi
    def render_html(self, docids, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name(self._template)
        docs = self.env[report.model].browse(docids)
        wizard_get_line = self.env['attendance.wizard'].new()
        float_to_time = self.env['hr.attendance'].float_to_time
        docargs = {
            'docs_ids': docids,
            'doc_model': report.model,
            'docs': docs,
            'data': data,
            'generate_line': wizard_get_line.generate_report_line,
            'float_to_time': float_to_time,
        }
        return report_obj.render(self._template, docargs)
