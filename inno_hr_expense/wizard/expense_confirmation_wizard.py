# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ExpenseConfirmation(models.TransientModel):
	_name = 'expense.confirmation'

	expense_sheet_id = fields.Many2one('hr.expense.sheet', string="Expense Report")
	consumed = fields.Float()
	budget = fields.Float()

	
