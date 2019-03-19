# -*- coding:utf-8 -*-
import logging
from odoo import SUPERUSER_ID, _, api, fields, models


# import mount_to_text
# from openerp.addons.amount_to_text_id

_log = logging.getLogger(__name__)

class CustomKwitansiPdf(models.AbstractModel):
    _name = 'report.pqm_leave_report.leave_report_template'
    _template = 'pqm_leave_report.leave_report_template'

    def gen_link_img(self, data_line):
        link = "https://image-charts.com/chart?"
        employee = []
        sick = []
        for line in data_line:
            employee.append(line.get('employee'))
            sick.append(line.get('sick'))
        var_chd = "a:" + ",".join([str(x) for x in sick])
        var_chxl = "0:|" + "".join([str(x).replace(" ", "%20").replace("'", "%27") + "|" for x in employee])
        variable = {
            "cht": "bvg",
            "chd": var_chd,
            "chs": "999x480",
            "chxt": "x,y",
            "chxl": var_chxl,
            "chf": "b0,lg,90,0038ff,1,44acec,0.2",
            "chtt": " ",
            "chma": "0,0,10,10",  # must last var
        }

        for key, val in variable.iteritems():
            link += key + "=" + val
            if key != "chma":
                link += "&"

        return link

    @api.multi
    def render_html(self, docids, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name(self._template)
        docs = self.env[report.model].browse(docids)
        wizard_get_line = self.env['leave.wizard'].new()
        data_line = wizard_get_line.generate_report_line(data.get('month'), data.get('year'))
        data.update({"link_chart": self.gen_link_img(data_line)})
        data.update({"list_sick": wizard_get_line.gen_sick_list(data_line)})
        docargs = {
            'docs_ids': docids,
            'doc_model': report.model,
            'docs': docs,
            'data': data,
            'data_line': data_line,
        }
        return report_obj.render(self._template, docargs)
