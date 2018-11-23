import base64
import io
from datetime import date, datetime, time, timedelta
from calendar import monthrange
from dateutil.rrule import rrule, DAILY

try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT,DEFAULT_SERVER_DATETIME_FORMAT
from odoo import models, fields, api, _
from odoo.exceptions import Warning


class LeaveWizard(models.TransientModel):
    _name = "leave.wizard"
    _description = "Leave Wizard"

    list_month = [(1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'), (5, 'May'),
                  (6, 'June'), (7, 'July'), (8, 'August'), (9, 'September'), (10, 'October'),
                  (11, 'November'), (12, 'December')]

    year = fields.Selection([(num, str(num)) for num in range(date.today().year - 2, date.today().year + 1)], default=date.today().year)
    month = fields.Selection(list_month, default=date.today().month)
    data_x = fields.Binary(string="File", readonly=True)

    def generate_report_line(self, month=None, year=None):
        month = int(month) if month else date.today().month
        year = int(year) if year else date.today().year
        employee_list = self.env['hr.employee'].search([('user_id', '!=', 1)])

        date_start = date(day=1, month=month, year=year)
        date_stop = date(day=monthrange(year, month)[1], month=month, year=year)
        leaves = self.env['hr.holidays'].search([('state', '=', 'validate'), ('type', '=', 'add'),
                                                 ('create_date', '<=', date_stop.strftime(DEFAULT_SERVER_DATE_FORMAT))])
        leave_request = self.env['hr.holidays'].search([('state', '=', 'validate'), ('type', '=', 'remove'),
                                                        ('date_from', '<=', date_stop.strftime(DEFAULT_SERVER_DATE_FORMAT)),
                                                        ('date_to', '>=', date_start.strftime(DEFAULT_SERVER_DATE_FORMAT))])
        leave_allocation = self.env['hr.holidays'].search([('state', '=', 'validate'), ('type', '=', 'add'),
                                                           ('create_date', '<=', date_stop.strftime(DEFAULT_SERVER_DATE_FORMAT)),
                                                           ('create_date', '>=', date_start.strftime(DEFAULT_SERVER_DATE_FORMAT))])
        leave_all = self.env['hr.holidays'].search([('state', '=', 'validate'), ('type', '=', 'remove')])
        
        result = []
        for employee in employee_list:
            if employee:
                working_days = employee.calendar_id
                list_day = working_days.mapped('attendance_ids') if working_days else False
                list_day = list_day.mapped("dayofweek") if list_day else []
                print list_day, employee.name
                dict_data = {
                    "employee": employee.name,
                    "request_year": 0,
                    "request": 0,
                    "reward": 0,
                    "allocation": 0,
                    "total": 0,
                    "total_reward": 0,
                    "leave_date": "",
                    "sick": 0,
                }
                leave_date = []
                for rec in leave_request:
                    start = datetime.strptime(rec.date_from, DEFAULT_SERVER_DATETIME_FORMAT).date()
                    end = datetime.strptime(rec.date_to, DEFAULT_SERVER_DATETIME_FORMAT).date()
                    if rec.employee_id.id == employee.id:
                        if start.month == end.month:
                            if rec.holiday_status_id.category == 'yearly':
                                dict_data["request_year"] += rec.number_of_days_temp
                            if rec.holiday_status_id.category == 'reward':
                                dict_data["reward"] += rec.number_of_days_temp
                            if rec.holiday_status_id.category == 'sick':
                                dict_data["sick"] += rec.number_of_days_temp
                        else:
                            for dt in rrule(DAILY, dtstart=start, until=end):
                                if str(dt.weekday()) in list_day and dt.date().month == month:
                                    if rec.holiday_status_id.category == 'yearly':
                                        dict_data["request_year"] += 1
                                    if rec.holiday_status_id.category == 'reward':
                                        dict_data["reward"] += 1
                                    if rec.holiday_status_id.category == 'sick':
                                        dict_data["sick"] += 1

                        if rec.holiday_status_id.category != 'sick':
                            for dt in rrule(DAILY, dtstart=start, until=end):
                                if str(dt.weekday()) in list_day and dt.month == month:
                                    leave_date.append(dt.day)
                for al in leave_allocation:
                    if al.employee_id.id == employee.id:
                        if al.holiday_status_id.category == 'yearly':
                            dict_data["allocation"] += al.number_of_days_temp

                for leave in leaves:
                    if leave.employee_id.id == employee.id:
                        if leave.holiday_status_id.category == 'yearly':
                            dict_data["total"] += leave.number_of_days_temp
                        if leave.holiday_status_id.category == 'reward':
                            dict_data["total_reward"] += leave.number_of_days_temp

                for leave in leave_all:
                    start = datetime.strptime(leave.date_from, DEFAULT_SERVER_DATETIME_FORMAT).date()
                    end = datetime.strptime(leave.date_to, DEFAULT_SERVER_DATETIME_FORMAT).date()
                    if leave.employee_id.id == employee.id:
                        if start.month == end.month and start.month < month and end.month < month:
                            if leave.holiday_status_id.category == 'yearly':
                                dict_data["total"] -= leave.number_of_days_temp
                            if leave.holiday_status_id.category == 'reward':
                                dict_data["total_reward"] -= leave.number_of_days_temp
                        elif start.month < month and end.month <= month:
                            for dt in rrule(DAILY, dtstart=start, until=end):
                                if str(dt.weekday()) in list_day and dt.date().month < month:
                                    if leave.holiday_status_id.category == 'yearly':
                                        dict_data["total"] -= 1
                                    if leave.holiday_status_id.category == 'reward':
                                        dict_data["total_reward"] -= 1

                str_leave_date = [str(x) for x in sorted(leave_date)]
                dict_data['request'] = len(leave_date)
                dict_data["total"] -= dict_data["request_year"]
                dict_data["total_reward"] -= dict_data["reward"]
                dict_data['leave_date'] = ", ".join(str_leave_date) if leave_date else ""
                result.append(dict_data)
        return result

    def gen_sick_list(self, data_line):
        list_sick = []
        dividen = len(data_line) / 3
        for line in data_line:
            list_sick.append((line.get('employee'), line.get('sick')))

        parent_list = []
        if list_sick:
            parent_list.append(list_sick[:dividen])
            parent_list.append(list_sick[dividen:dividen * 2])
            parent_list.append(list_sick[dividen*2:])

        return parent_list

    def print_pdf(self):
        data = {}
        data['month'] = self.month
        data['year'] = self.year
        data['month_str'] = dict(self.list_month).get(self.month)
        report_dict = self.env['report'].get_action(self, 'pqm_leave_report.leave_report_template', data=data)
        return report_dict

    def print_xls(self):
        report_line = self.generate_report_line(self.month, self.year)
        month_str = dict(self.list_month).get(self.month)

        bytes_control = io.BytesIO()
        workbook = xlsxwriter.Workbook(bytes_control)
        filename = 'Leave Report %s %s.xlsx' % (month_str, self.year)

        worksheet = workbook.add_worksheet("Leave Report")

        # style
        title = workbook.add_format({'bold': 1, 'align': 'center', 'valign': 'vcenter'})
        title.set_font_size('16')
        title.set_font_name('Arial')

        header = workbook.add_format({'bold': 1, 'align': 'center', 'valign': 'vcenter', 'border': 1})
        header.set_text_wrap()
        header.set_font_size('12')
        header.set_font_name('Arial')

        name = workbook.add_format({'bold': 1, 'align': 'left', 'border': 1})
        name.set_text_wrap()
        name.set_font_size('10')
        name.set_font_name('Arial')

        cel_blank = workbook.add_format({'bold': 0, 'align': 'center', 'border': 1})
        cel_blank.set_font_size('10')
        cel_blank.set_font_name('Arial')
        cel_blank.set_text_wrap()

        cel_yellow = workbook.add_format({'bold': 0, 'align': 'center', 'border': 1})
        cel_yellow.set_font_size('10')
        cel_yellow.set_font_name('Arial')
        cel_yellow.set_bg_color('#fbff00')
        cel_yellow.set_text_wrap()

        cel_sick_header = workbook.add_format({'bold': 1, 'align': 'center', 'border': 1})
        cel_sick_header.set_font_size('10')
        cel_sick_header.set_font_name('Arial')
        cel_sick_header.set_text_wrap()

        cel_sick_employee = workbook.add_format({'bold': 0, 'align': 'left', 'border': 1})
        cel_sick_employee.set_font_size('10')
        cel_sick_employee.set_font_name('Arial')
        cel_sick_employee.set_text_wrap()

        # set width coloumn and row
        worksheet.set_column('B:B', 28)
        worksheet.set_column('C:Q', 12)
        worksheet.set_row(1, 30)
        worksheet.set_row(2, 43)

        # set value
        worksheet.merge_range('B2:I2', 'Leave Report %s %s' % (month_str, self.year), title)
        worksheet.merge_range('B3:B4', 'PQM Members', header)
        worksheet.write('C3', 'Ambil Cuti', header)
        worksheet.write('D3', 'Potong Cuti Reward', header)
        worksheet.write('E3', 'Tambahan Cuti Tahunan', header)
        worksheet.write('F3', 'Sisa Cuti Tahunan', header)
        worksheet.write('G3', 'Sisa Cuti Reward', header)
        worksheet.write('H3', 'Tanggal Cuti', header)
        x = ord('C')
        for i in range(0, 6):
            worksheet.write(chr(x+i) + str(4), 'Times', header)
        x = 5
        list_sick = self.gen_sick_list(report_line)
        for line in report_line:
            worksheet.write('B'+str(x), line['employee'], name)
            worksheet.write('C'+str(x), line['request'], cel_blank if line['request'] == 0 else cel_yellow)
            worksheet.write('D'+str(x), line['reward'], cel_blank if line['reward'] == 0 else cel_yellow)
            worksheet.write('E'+str(x), line['allocation'], cel_blank if line['allocation'] == 0 else cel_yellow)
            worksheet.write('F'+str(x), line['total'], cel_blank if line['total'] == 0 else cel_yellow)
            worksheet.write('G'+str(x), line['total_reward'], cel_blank if line['total_reward'] == 0 else cel_yellow)
            worksheet.write('H'+str(x), line['leave_date'], cel_blank if line['leave_date'] == "" else cel_yellow)
            x += 1

        x += 26
        chart = workbook.add_chart({'type': 'column'})
        worksheet.write('A'+str(x), 'No', cel_sick_header)
        worksheet.write('B' + str(x), 'Employee', cel_sick_header)
        worksheet.write('C' + str(x), 'Sick', cel_sick_header)

        worksheet.write('E' + str(x), 'No', cel_sick_header)
        worksheet.merge_range('F' + str(x) + ':' + 'G' + str(x), 'Employee', cel_sick_header)
        worksheet.write('H' + str(x), 'Sick', cel_sick_header)

        worksheet.write('J' + str(x), 'No', cel_sick_header)
        worksheet.merge_range('K' + str(x) + ':' + 'L' + str(x), 'Employee', cel_sick_header)
        worksheet.write('M' + str(x), 'Sick', cel_sick_header)

        x += 1
        idx_no = 1
        for i in range(x, x + len(list_sick[0])):
            worksheet.write('A' + str(i), idx_no, cel_blank)
            worksheet.write('B' + str(i), list_sick[0][i-x][0], cel_sick_employee)
            worksheet.write('C' + str(i), list_sick[0][i-x][1], cel_blank)
            idx_no += 1

        for i in range(x, x + len(list_sick[1])):
            worksheet.write('E' + str(i), idx_no, cel_blank)
            worksheet.merge_range('F' + str(i) + ':' + 'G' + str(i), list_sick[1][i-x][0], cel_sick_employee)
            worksheet.write('H' + str(i), list_sick[1][i-x][1], cel_blank)
            idx_no += 1

        for i in range(x, x + len(list_sick[2])):
            worksheet.write('J' + str(i), idx_no, cel_blank)
            worksheet.merge_range('K' + str(i) + ':' + 'L' + str(i), list_sick[2][i-x][0], cel_sick_employee)
            worksheet.write('M' + str(i), list_sick[2][i-x][1], cel_blank)
            idx_no += 1

        chart.add_series({
            'name': "='%s'!$C$%s" % (worksheet.name, x - 1),
            'categories': "='%s'!$B$%s:$B$%s,'%s'!$F$%s:$F$%s,'%s'!$K$%s:$K$%s" % (
            worksheet.name, x, x + len(list_sick[0]) - 1, worksheet.name, x, x + len(list_sick[1]) - 1,
            worksheet.name, x, x + len(list_sick[2]) - 1),
            'values': "='%s'!$C$%s:$C$%s,'%s'!$H$%s:$H$%s,'%s'!$M$%s:$M$%s" % (
            worksheet.name, x, x + len(list_sick[0]) - 1, worksheet.name, x, x + len(list_sick[1]) - 1,
            worksheet.name, x, x + len(list_sick[2]) - 1)
        })
        chart.set_size({'x_scale': 2.5, 'y_scale': 1.5})

        chart.set_title({'name': 'Sick Report %s %s' % (month_str, self.year)})
        chart.set_x_axis({'name': 'Employee'})
        chart.set_y_axis({'name': 'Sick'})
        chart.set_style(11)
        worksheet.insert_chart('A'+str(x-25), chart, {'x_offset': 25, 'y_offset': 10})

        workbook.close()
        out = base64.encodestring(bytes_control.getvalue())
        self.write({'data_x': out})

        return {
            "type": "ir.actions.act_url",
            "url": "/web/content?model=leave.wizard&field=data_x&filename_field=filename&id=%s&download=true&filename=%s" % (self.id, filename),
            "target": "current",
        }







