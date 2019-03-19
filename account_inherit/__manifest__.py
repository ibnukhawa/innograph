# -*- coding: utf-8 -*-
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
    'name' : 'Account Inherit',
    'version' : '1.0',
    'summary': 'Adjust small things in accounting',
    'description': """
v1.0
- show journal items menu for accounting not have to debug 
    """,
    'author' : 'Port Cities, Ltd',
    'category': 'Accounting',
    'depends' : ['account'],
    'data': [
         'views/account_view.xml',        
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

