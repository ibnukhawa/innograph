# pylint: disable=import-error,protected-access,too-few-public-methods
"""Inherit HR Holidays"""
from odoo import api, models, fields, _
import pytz


class HrHolidays(models.Model):
    """Send Email when requesting / approving leaves"""
    _inherit = "hr.holidays"

    coach_id = fields.Many2one('hr.employee', related="employee_id.coach_id")

    def action_message_leave_request(self):
        """ Method to sent email of leave request"""
        template = self.env.ref('pqm_portal_leave.mail_template_leave_request')
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        if self.employee_id.coach_id:
            recipients = [self.employee_id.coach_id]
            tz = self.employee_id.user_id.partner_id.tz or pytz.utc
            for recipient in recipients:
                ctx = ({
                    'email_to': recipient.user_id.email if recipient.user_id else "-",
                    'employee': self.employee_id.name,
                    'manager': recipient.name,
                    'leave_type': self.holiday_status_id.name,
                    'duration': self.number_of_days_temp,
                    'date_from': fields.Datetime.to_string(fields.Datetime.context_timestamp(self.with_context(tz=tz), fields.Datetime.from_string(self.date_from)))[:16],
                    'date_to': fields.Datetime.to_string(fields.Datetime.context_timestamp(self.with_context(tz=tz), fields.Datetime.from_string(self.date_to)))[:16],
                    'description': self.name,
                    'summary': self._get_summary_leave(),
                    'leave_url': '%s/leaves/approval' % base_url
                })
                template.with_context(ctx).send_mail(self.id, force_send=True)
        return True

    def action_message_leave_approve(self, state):
        """ Method to sent email of leave approval"""
        template = self.env.ref('pqm_portal_leave.mail_template_leave_approve')
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        recipient = self.employee_id
        tz = self.employee_id.user_id.partner_id.tz or pytz.utc
        ctx = ({
            'email_to': recipient.user_id.email if recipient.user_id else "-",
            'employee': self.employee_id.name,
            'coach': self.employee_id.coach_id.name,
            'leave_type': self.holiday_status_id.name,
            'duration': self.number_of_days_temp,
            'date_from': fields.Datetime.to_string(fields.Datetime.context_timestamp(self.with_context(tz=tz), fields.Datetime.from_string(self.date_from)))[:16],
            'date_to': fields.Datetime.to_string(fields.Datetime.context_timestamp(self.with_context(tz=tz), fields.Datetime.from_string(self.date_to)))[:16],
            'description': self.name,
            'report_note': self.report_note if self.report_note else '',
            'state': state,
            'summary': self._get_summary_leave(),
            'leave_url': '%s/my/leaves/' % base_url
        })
        template.with_context(ctx).send_mail(self.id, force_send=True)
        return True

    def action_message_leave_limit(self):
        """ Method to sent email of leave limit"""
        template = self.env.ref('pqm_portal_leave.mail_template_leave_limit')
        recipient = self.employee_id
        ctx = ({
            'email_to': recipient.user_id.email if recipient.user_id else "-",
            'employee': self.employee_id.name
        })
        template.with_context(ctx).send_mail(self.id, force_send=True)
        return True

    @api.model
    def create(self, values):
        """Override the function to sent email when creating leave request"""
        res = super(HrHolidays, self).create(values)
        if values.get('type') == 'remove':
            res.action_message_leave_request()
        return res

    @api.multi
    def write(self, values):
        for leave in self:
            if leave.type == 'remove' and values.get('state') in ['refuse', 'validate']:
                leave.action_message_leave_approve(values.get('state'))
        return super(HrHolidays, self).write(values)

    @api.multi
    def action_validate(self):
        """Override the function to sent email when validating yearly leave"""
        # TODO: change hardcoded id of leave
        if self.type == 'add' and self.holiday_status_id.id == 5:
            limit = self.search([('employee_id', '=', self.employee_id.id), 
                ('holiday_status_id', '=', 5),
                ('type', '=', self.type),
                ('state', '=', 'validate')])
            yearly_limit = self.number_of_days_temp
            for rec in limit:
                yearly_limit += rec.number_of_days_temp
            if yearly_limit >= 20:
                self.action_message_leave_limit()
            if yearly_limit > 24:
                self.number_of_days_temp = 0
        return super(HrHolidays, self).action_validate()

    def _get_summary_leave(self):
        types = []
        leave_type = self.env['hr.holidays.status'].sudo().search([])
        for leave in leave_type:
            domain = [
                ('employee_id', '=', self.employee_id.id),
                ('holiday_status_id', '=', leave.id),
                ('type', '=', 'add'),
                ('state', '=', 'validate')
            ]
            lines = self.sudo().search(domain)
            allocation = sum(line.number_of_days_temp for line in lines)

            domain = [
                ('employee_id', '=', self.employee_id.id),
                ('holiday_status_id', '=', leave.id),
                ('type', '=', 'remove'),
                ('state', '=', 'validate')
            ]
            lines = self.sudo().search(domain)
            total = sum(line.number_of_days for line in lines)

            remaining = allocation + total
            if allocation != 0.0 or total != 0.0:
                if not leave.show_deficit:
                    remaining = 0.0 if remaining < 0.0 else remaining
                types.append({
                    'name': leave.name,
                    'days': '%.2f' % allocation,
                    'total_days': '%.2f' % abs(total),
                    'remaining_days': '%.2f' % remaining,
                })
        return types