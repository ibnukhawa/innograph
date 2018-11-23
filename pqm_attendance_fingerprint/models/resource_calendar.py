from odoo import fields, api, models, _


class ResourceCalendarLate(models.Model):
    _name = "resource.calendar.late"
    _order = "minutes"

    punishment = fields.Char("Punishment")
    minutes = fields.Float("Minutes")
    calendar_id = fields.Many2one('resource.calendar')


class ResourceCalendar(models.Model):
    _inherit = "resource.calendar"

    late_ids = fields.One2many('resource.calendar.late', 'calendar_id', string="Late")

    @api.multi
    def write(self, vals):
        if vals.get("attendance_ids"):
            rule_use = []
            for rule_attendan in vals.get("attendance_ids"):
                if rule_attendan[0] == 1:
                    cal_attend_list = self.env['resource.calendar.attendance'].browse(rule_attendan[1])
                    rule_use.append({
                        "dayofweek": cal_attend_list.dayofweek,
                        "hour_from": rule_attendan[2].get("hour_from") and rule_attendan[2].get("hour_from") or cal_attend_list.hour_from,
                        "hour_to": rule_attendan[2].get("hour_to") and rule_attendan[2].get("hour_to") or cal_attend_list.hour_to,
                    })

                elif rule_attendan[0] == 0:
                    rule_use.append(rule_attendan[2])
            list_day = [rule.get("dayofweek", 0) for rule in rule_use]
            employe_used = self.env['hr.employee'].search([("calendar_id", '=', self.id)])
            attendants = self.env['hr.attendance'].search([("day_of_week", "in", list_day), ("employee_id", "in", employe_used.ids)])
            for attendant in attendants:
                for rule in rule_use:
                    if int(attendant.day_of_week) == int(rule.get("dayofweek", 0)):
                        attendant.write({
                            "plan_in": rule.get("hour_from"),
                            "plan_out": rule.get("hour_to"),
                        })
        return super(ResourceCalendar, self).write(vals)