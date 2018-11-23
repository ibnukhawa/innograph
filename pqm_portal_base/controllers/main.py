# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from datetime import datetime, date, timedelta
from calendar import monthrange
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
import pytz
import werkzeug
from odoo.addons.website_portal.controllers.main import website_account


class WebsiteAccount(website_account):

    def _prepare_portal_layout_values(self):
        res = super(WebsiteAccount, self)._prepare_portal_layout_values()
        return res

   
