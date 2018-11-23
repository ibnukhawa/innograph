# coding: utf-8
##############################################################################
#
# This module is developed by Portcities Indonesia
# Copyright (C) 2017 Portcities Indonesia (<http://idealisconsulting.com>).
# All Rights Reserved
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name' : 'Profit & Loss Club PQM',
    'version' : '1.0',
    'summary': 'Profit & Loss Report',
    'description': """ Report configuration can be found under ~/static/src/xml/pqm_configuration.txt """,
    'author' : 'Port Cities',
    'category': 'report',
    'depends' : ['account'],
    'data': [
        'views/pqm_report.xml',
        'report/financial_report_paper.xml',
        'views/account_financial_report_view.xml',
        'wizard/accounting_report_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

