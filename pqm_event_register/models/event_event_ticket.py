# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
import pytz


class EventEventTicket(models.Model):
    _inherit = "event.event.ticket"

    def _deadline_date(self):
        event = self.event_id
        date = fields.Datetime.from_string(self.deadline).replace(tzinfo=pytz.utc).astimezone(pytz.timezone(event.date_tz or 'UTC'))
        return date.strftime('%d %b %Y')

