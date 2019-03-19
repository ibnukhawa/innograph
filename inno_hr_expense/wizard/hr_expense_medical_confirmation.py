# -*- coding: utf-8 -*-
""" Import """
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class HrExpenseMedicalConfirmation(models.TransientModel):
	""" HR Expense Medical Confirmation """
	_name = 'hr.expense.medical.confirmation'

	expense_request = fields.Float()
	medical_budget = fields.Float()
	sheet_id = fields.Many2one('hr.expense.sheet')
	employee_name = fields.Char(related="sheet_id.employee_id.name")

	@api.multi
	def confirm_validate(self):
		""" Confirmation to continue """
		self.ensure_one()
		if self.sheet_id:
			if self.sheet_id.state == 'submit':
				self.sheet_id.with_context(medical_expense_confirmed=True).validate_expense_sheets()
			elif self.sheet_id.state == 'validate':
				self.sheet_id.with_context(medical_expense_confirmed=True).approve_expense_sheets()
			else:
				raise UserError(_("Expense not in state Submitted/Validated."))

