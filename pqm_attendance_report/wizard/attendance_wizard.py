import base64
import io
import pytz
from datetime import date, datetime, time
from calendar import monthrange
from dateutil.rrule import rrule, DAILY

try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT,DEFAULT_SERVER_DATETIME_FORMAT
from odoo import models, fields, api, _
from odoo.exceptions import Warning


class AttendanceWizard(models.TransientModel):
    _name = "attendance.wizard"
    _description = "Attendance Wizard"

    list_month = [(1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'), (5, 'May'),
                  (6, 'June'), (7, 'July'), (8, 'August'), (9, 'September'), (10, 'October'),
                  (11, 'November'), (12, 'December')]

    year = fields.Selection([(num, str(num)) for num in range(date.today().year - 2, date.today().year + 1)], default=date.today().year)
    month = fields.Selection(list_month, default=date.today().month)
    data_x = fields.Binary(string="File", readonly=True)
    extra_meal_time = fields.Float("Extra Meal Time", default=18.5)
    extra_meal_price = fields.Float("Extra Meal Price", default=40000.0)

    def generate_report_line(self, month=None, year=None, meal=None):
        month = int(month) if month else date.today().month
        year = int(year) if year else date.today().year
        meal = float(meal) if meal else 0
        employee_list = self.env['hr.employee'].search([('user_id', '!=', 1)])

        date_start = date(day=1, month=month, year=year)
        date_stop = date(day=monthrange(year, month)[1], month=month, year=year)
        domain = [
            ("date", "<=", date_stop.strftime(DEFAULT_SERVER_DATE_FORMAT)),
            ("date", ">=", date_start.strftime(DEFAULT_SERVER_DATE_FORMAT)),
        ]
        attendances = self.env['hr.attendance'].search(domain)

        sick_type = self.env['hr.holidays.status'].search(["|", ("name", "ilike", "sick"), ("name", "ilike", "sakit")])
        leaves = self.env['hr.holidays'].search(['&', ('state', '=', 'validate'), '|', '&',
                                                 ("date_from", '<=', date_stop.strftime(DEFAULT_SERVER_DATETIME_FORMAT)),
                                                 ("date_from", '>=', date_start.strftime(DEFAULT_SERVER_DATETIME_FORMAT)),
                                                 '&', ("date_to", '<=', date_stop.strftime(DEFAULT_SERVER_DATETIME_FORMAT)),
                                                 ("date_to", '>=',date_start.strftime(DEFAULT_SERVER_DATETIME_FORMAT))])
        result = []

        for employee in employee_list:
            if employee:
                emp_working_time = employee.calendar_id
                emp_work_rule = emp_working_time.attendance_ids if emp_working_time else False
                emp_work_days = emp_work_rule.mapped("dayofweek") if emp_work_rule else False
                if not emp_work_days:
                    emp_work_days = []
                dict_data = {
                    "employee": employee.name,
                    "check_in": 0,
                    "check_out": 0,
                    "late": 0,
                    "sick": 0,
                    "leave": 0,
                    "outside": 0,
                    "attend": 0,
                    "meal": 0,
                }
                for dt in rrule(DAILY, dtstart=date_start, until=date_stop):
                    dt_str = dt.strftime(DEFAULT_SERVER_DATE_FORMAT)
                    dt.replace(hour=10)
                    # TODO: fix later this singleton issue
                    emp_attend = attendances.filtered(lambda x: x.employee_id.id == employee.id and x.date == dt_str)
                    emp_attend = emp_attend.sorted(lambda x: x.id)
                    emp_attend = emp_attend[0] if emp_attend else emp_attend
                    leave_emp = leaves.filtered(lambda x: x.employee_id.id == employee.id and str(x.date_from).split(" ")[0] <= dt_str <= str(x.date_to).split(" ")[0])
                    leave_emp = leave_emp.sorted(lambda x: x.id)
                    leave_emp = leave_emp[0] if leave_emp else leave_emp
                    if unicode(str(dt.weekday()), "utf-8") in emp_work_days and dt <= datetime.now():
                        if leave_emp:
                            if leave_emp.holiday_status_id.id in sick_type.ids:
                                dict_data["sick"] += 1
                            else:
                                dict_data["leave"] += 1
                        elif emp_attend:
                            # compute extra meal
                            user = emp_attend.employee_id.user_id
                            meal_add = 0
                            tz = pytz.timezone(user.tz) if user.tz else pytz.utc
                            meal_hour = int(meal) if meal else 0
                            meal_minute = int(meal % 1 * 60) if meal else 0
                            meal_time_check = meal_hour or meal_minute
                            if emp_attend.check_out and meal_time_check and meal_hour > 0 and not emp_attend.employee_id.is_consultant:
                                date_meal = tz.localize(dt.replace(hour=meal_hour, minute=meal_minute)).astimezone(pytz.utc)
                                check_out = pytz.utc.localize(datetime.strptime(emp_attend.check_out,DEFAULT_SERVER_DATETIME_FORMAT))
                                meal_add = 1 if check_out >= date_meal else 0
                            dict_data["meal"] += meal_add

                            if not emp_attend.auto_attendance:
                                add_out = 1 if emp_attend.status == "check_out_empty" else 0
                                add_late = 1 if emp_attend.status in ["check_in_late", "in_late_out_early"] else 0
                                dict_data["check_out"] += add_out
                                dict_data["late"] += add_late
                                dict_data["attend"] += 1
                            else:
                                dict_data["check_in"] += 1
                                dict_data["check_out"] += 1
                        else:
                            dict_data["check_in"] += 1
                            dict_data["check_out"] += 1

                        # dinas luar
                        if emp_attend.work_outside:
                            dict_data["outside"] += 1
                result.append(dict_data)
        return result

    def print_pdf(self):
        data = {}
        data['month'] = self.month
        data['year'] = self.year
        data['meal_float'] = self.extra_meal_time
        data['month_str'] = dict(self.list_month).get(self.month)
        data['meal_price'] = self.extra_meal_price
        report_dict = self.env['report'].get_action(self, 'pqm_attendance_report.attendance_report_template', data=data)
        return report_dict

    def print_xls(self):
        report_line = self.generate_report_line(self.month, self.year, self.extra_meal_time)
        month_str = dict(self.list_month).get(self.month)
        meal_line = []

        bytes_control = io.BytesIO()
        workbook = xlsxwriter.Workbook(bytes_control)
        filename = 'Attendance Report %s %s.xlsx' % (month_str, self.year)

        worksheet = workbook.add_worksheet("Attendance Report xls")
        worksheet_meal = workbook.add_worksheet("Makan Malam Report xls")

        # style
        title = workbook.add_format({'bold': 1, 'align': 'center', 'valign': 'vcenter'})
        title.set_font_size('16')
        title.set_font_name('Arial')

        header = workbook.add_format({'bold': 1, 'align': 'center', 'valign': 'vcenter', 'border': 1})
        header.set_text_wrap()
        header.set_font_size('12')
        header.set_font_name('Arial')

        header_meal = workbook.add_format({'bold': 1, 'align': 'center', 'valign': 'vcenter', 'border': 1})
        header_meal.set_text_wrap()
        header_meal.set_font_size('10')
        header_meal.set_font_name('Arial')

        period = workbook.add_format({'bold': 1, 'align': 'center', 'valign': 'vcenter', 'border': 0})
        period.set_text_wrap()
        period.set_font_size('12')
        period.set_font_name('Arial')

        name = workbook.add_format({'bold': 1, 'align': 'left', 'border': 1})
        name.set_text_wrap()
        name.set_font_size('10')
        name.set_font_name('Arial')

        cel_blank = workbook.add_format({'bold': 0, 'align': 'center', 'border': 1})
        cel_blank.set_font_size('10')
        cel_blank.set_font_name('Arial')

        cel_yellow = workbook.add_format({'bold': 0, 'align': 'center', 'border': 1})
        cel_yellow.set_font_size('10')
        cel_yellow.set_font_name('Arial')
        cel_yellow.set_bg_color('#fbff00')

        cel_red = workbook.add_format({'bold': 0, 'align': 'center', 'border': 1})
        cel_red.set_font_size('10')
        cel_red.set_font_name('Arial')
        cel_red.set_bg_color('#ff2b2b')

        cel_price = workbook.add_format({'bold': 0, 'align': 'right', 'border': 1})
        cel_price.set_font_size('10')
        cel_price.set_font_name('Arial')
        cel_price.set_num_format('#,##0')

        total_price = workbook.add_format({'bold': 1, 'align': 'right', 'valign': 'vcenter', 'border': 1})
        total_price.set_text_wrap()
        total_price.set_font_size('10')
        total_price.set_font_name('Arial')
        total_price.set_num_format('#,##0')

        note_meal = workbook.add_format({'bold': 0, 'align': 'left', 'valign': 'vcenter', 'border': 0})
        note_meal.set_font_size('10')
        note_meal.set_font_name('Arial')

        # set width coloumn and row
        worksheet.set_column('B:B', 28)
        worksheet.set_column('C:J', 12)
        worksheet.set_row(1, 30)
        worksheet.set_row(2, 31)

        # set value
        worksheet.merge_range('B2:J2', 'Attendance Report %s %s' % (month_str, self.year), title)
        worksheet.merge_range('B3:B4', 'PQM Members', header)
        worksheet.write('C3', 'Terlambat', header)
        worksheet.write('D3', 'Personal Izin', header)
        worksheet.write('E3', 'Dinas Luar', header)
        worksheet.write('F3', 'Tidak Absen Datang', header)
        worksheet.write('G3', 'Tidak Absen Pulang', header)
        worksheet.write('H3', 'Sakit', header)
        worksheet.write('I3', 'Cuti', header)
        worksheet.write('J3', 'Absen', header)
        x = ord('C')
        for i in range(0, 8):
            worksheet.write(chr(x+i) + str(4), 'Times', header)
        x = 5
        for line in report_line:
            worksheet.write('B'+str(x), line['employee'], name)
            worksheet.write('C'+str(x), line['late'], cel_blank if line['late'] == 0 else cel_yellow if 0 < line['late'] <= 5 else cel_red)
            worksheet.write('D'+str(x), 0, cel_blank)
            worksheet.write('E'+str(x), line['outside'], cel_blank)
            worksheet.write('F'+str(x), line['check_in'], cel_blank if line['check_in'] == 0 else cel_yellow if 0 < line['check_in'] <= 5 else cel_red)
            worksheet.write('G'+str(x), line['check_out'], cel_blank if line['check_out'] == 0 else cel_yellow if 0 < line['check_out'] <= 5 else cel_red)
            worksheet.write('H'+str(x), line['sick'], cel_blank if line['sick'] == 0 else cel_yellow if 0 < line['sick'] <= 5 else cel_red)
            worksheet.write('I'+str(x), line['leave'], cel_blank if line['leave'] == 0 else cel_yellow if 0 < line['leave'] <= 5 else cel_red)
            worksheet.write('J'+str(x), line['attend'], cel_blank)
            if line['meal'] != 0:
                meal_line.append({'employee': line['employee'], 'meal': line['meal']})

            x += 1

        x += 1

        # set width coloumn and row
        worksheet_meal.set_column('B:B', 6)
        worksheet_meal.set_column('C:C', 45)
        worksheet_meal.set_column('D:D', 15)
        worksheet_meal.set_column('E:E', 20)
        worksheet_meal.set_row(1, 30)

        worksheet_meal.merge_range('B2:E2', 'DATA KLAIM MAKAN MALAM KARYAWAN PQM', title)
        worksheet_meal.merge_range('B4:E4', 'PERIODE: %s %s' % (month_str, self.year), period)

        x = 6
        worksheet_meal.write('B' + str(x), 'NO', header_meal)
        worksheet_meal.write('C' + str(x), 'NAMA KARYAWAN', header_meal)
        worksheet_meal.write('D' + str(x), 'JUMLAH ABSEN', header_meal)
        worksheet_meal.write('E' + str(x), 'TOTAL', header_meal)
        x+=1

        meal_count = 0
        for line in meal_line:
            worksheet_meal.write('B' + str(x), x - 6, cel_blank)
            worksheet_meal.write('C' + str(x), line.get('employee'), name)
            worksheet_meal.write('D' + str(x), line.get('meal'), cel_blank)
            worksheet_meal.write('E' + str(x), line.get('meal', 0) * self.extra_meal_price, cel_price)
            meal_count += line.get('meal')
            x += 1

        worksheet_meal.merge_range('B' + str(x) + ":" + 'C' + str(x), 'TOTAL UANG MAKAN MALAM BULAN %s' % month_str.upper(), header_meal)
        worksheet_meal.write_formula('D' + str(x), '=SUM(D7:D%s)' % str(x-1), header_meal, meal_count)
        worksheet_meal.write_formula('E' + str(x), '=SUM(E7:E%s)' % str(x-1), total_price, meal_count * self.extra_meal_price)

        x += 2
        worksheet_meal.write('B'+str(x), 'NOTE: ', note_meal)
        worksheet_meal.write('B' + str(x+1), '1. Jam Makan Malam pada %s' % self.env['hr.attendance'].float_to_time(self.extra_meal_time), note_meal)
        worksheet_meal.write('B' + str(x+2), '2. Harga Makan Malam Rp %s / pack' % '{0:,}'.format(int(self.extra_meal_price)), note_meal)

        workbook.close()
        out = base64.encodestring(bytes_control.getvalue())
        self.write({'data_x': out})

        return {
            "type": "ir.actions.act_url",
            "url": "/web/content?model=attendance.wizard&field=data_x&filename_field=filename&id=%s&download=true&filename=%s" % (self.id, filename),
            "target": "current",
        }







