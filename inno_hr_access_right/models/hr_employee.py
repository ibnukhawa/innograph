from odoo import api, models


class HrEmployee(models.Model):
	_inherit = 'hr.employee'

	@api.model
	def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
		access = self._context.get('access_from_employee_menu', False)
		if access:
			user = self.env.user
			if not self.user_has_groups('hr.group_hr_manager'):
				domain.append(('user_id', '=', user.id))
		return super(HrEmployee, self).search_read(domain, fields, offset, limit, order)