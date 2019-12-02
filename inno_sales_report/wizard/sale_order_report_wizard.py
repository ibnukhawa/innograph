# -*- coding: utf-8 -*-
import base64
import time
from cStringIO import StringIO
import xlsxwriter

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import date, datetime

class SaleOrderReportWizard(models.TransientModel):
	_name = "sale.order.report.wizard"

	@api.model
	def default_get(self, fields):
		res = super(SaleOrderReportWizard, self).default_get(fields)
		date = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")
		res.update({
			'date_from': date,
			'date_to': date,
		})
		return res

	date_from = fields.Datetime()
	date_to = fields.Datetime()
	categ_id = fields.Many2one('product.category', string="Category")
	team_id = fields.Many2one('crm.team', string="Sales Team")
	product_id = fields.Many2one('product.product', string="Product")
	user_id = fields.Many2one('res.users', string="Sales Person")
	state = fields.Selection([('draft', 'Quotation'), 
							  ('sent', 'Quotation Sent'),
							  ('waiting_for_approval', 'Waiting for Approval'),
							  ('sale', 'Sales Order'),
							  ('done', 'Locked'),
							  ('cancel', 'Cancelled')], default='sale', string="Status")
	filter_by = fields.Selection([('category', 'Category'),
								  ('salesperson', 'Salesperson')])


	report = fields.Binary('File', readonly=True)
	name = fields.Char('File Name', readonly=True)
	is_download = fields.Boolean(default=False)


	def _get_category(self, categ):
		if categ.mapped('child_id'):
			return categ + self._get_category(categ.mapped('child_id'))
		else:
			return categ

	def action_generate_report(self):
		report = StringIO()
		workbook = xlsxwriter.Workbook(report)
		filename = 'Sales Report.xlsx'

		sheet1 = workbook.add_worksheet('Sheet1')

		sale_obj = self.env['sale.order']
		domain = [
			('date_order', '>=', self.date_from),
			('date_order', '<=', self.date_to)
		]
		if self.team_id:
			domain.append(('team_id', '=', self.team_id.id))
		if self.user_id:
			domain.append(('user_id', '=', self.user_id.id))
		if self.state:
			domain.append(('state', '=', self.state))
		sale_src = sale_obj.search(domain)

		allowed_categ_ids = self._get_category(self.categ_id)

		header = workbook.add_format({'bold': 1, 'align': 'center'})
		header.set_align('vcenter')
		header.set_border()

		normal_left = workbook.add_format({'align': 'left'})
		normal_left.set_align('vcenter')
		normal_left.set_border()

		normal_center = workbook.add_format({'align': 'center'})
		normal_center.set_align('vcenter')
		normal_center.set_border()

		normal_number = workbook.add_format({'align': 'right'})
		normal_number.set_num_format('#,##0_);(#,##0)')
		normal_number.set_align('vcenter')
		normal_number.set_border()

		sheet1.set_column(0, 1, 20)
		sheet1.set_column(2, 2, 50)
		sheet1.set_column(3, 3, 20)
		sheet1.set_column(4, 4, 90)
		sheet1.set_column(5, 6, 10)
		sheet1.set_column(7, 8, 20)
		sheet1.set_column(9, 9, 10)
		sheet1.set_column(10, 11, 20)
		sheet1.set_column(12, 12, 10)
		sheet1.set_column(13, 14, 20)
		sheet1.set_column(15, 15, 30)
		sheet1.set_column(16, 16, 50)
		sheet1.set_column(17, 17, 20)
		sheet1.set_column(18, 18, 40)
		sheet1.set_column(19, 19, 30)
		sheet1.set_column(20, 20, 10)

		header_str = [
			'SO Number', 'Order Date', 'Name Customer', 'ID Product', 
			'Nama Product', 'Qty', 'Satuan', 'Harga Satuan', 'Discount (%)', 
			'Tax', 'Tax Amount', 'Amount', 'Discount', 'Sub Total', 'Total', 
			'Tax Name', 'Product Category', 'Payment Term', 'Sales Team/Display Name', 
			'Salesperson/Display Name', 'Status'
		]

		states = {
			'draft': 'Quotation',
			'sent': 'Quotation Sent',
			'waiting_for_approval': 'Waiting for Approval',
			'sale': 'Sales Order',
			'done': 'Locked',
			'cancel': 'Cancelled'
		}

		row = 0
		col = 0
		for head in header_str:
			sheet1.write(row, col, head, header)
			col += 1
		row += 1

		amt_per_categ = {}
		amt_per_salesperson = {}
		for sale in sale_src:
			x = 0
			order_line = sale.order_line
			if self.categ_id:
				order_line = order_line.filtered(lambda o: o.product_id.categ_id.id in allowed_categ_ids.ids)
			if self.product_id:
				order_line = order_line.filtered(lambda o: o.product_id.id == self.product_id.id)
			for line in order_line:
				taxes = {}
				for tax in line.tax_id:
					taxes[tax.name] = tax.amount
				product_name = line.product_id and line.product_id.display_name or ""
				product_name = product_name.split("[%s] " % (line.product_id and line.product_id.default_code or ""))

				sheet1.write(row, 0, sale.name, normal_center)
				sheet1.write(row, 1, sale.date_order, normal_center)
				sheet1.write(row, 2, sale.partner_id.name, normal_left)
				sheet1.write(row, 3, line.product_id.default_code, normal_left)
				sheet1.write(row, 4, product_name and product_name[1] or line.product_id.display_name, normal_left)
				sheet1.write(row, 5, line.product_uom_qty, normal_number)
				sheet1.write(row, 6, line.product_uom.name, normal_left)
				sheet1.write(row, 7, line.price_unit, normal_number)
				sheet1.write(row, 8, line.discount, normal_center)
				sheet1.write(row, 9, ",".join([str(taxes[i]) for i in taxes]), normal_center)
				sheet1.write(row, 10, line.price_tax, normal_number)
				sheet1.write(row, 11, not x and sale.amount or "", normal_number)
				sheet1.write(row, 12, "", normal_center)
				sheet1.write(row, 13, line.price_subtotal, normal_number)
				sheet1.write(row, 14, not x and sale.amount_total or "", normal_number)
				sheet1.write(row, 15, ",".join([i for i in taxes]), normal_center)
				sheet1.write(row, 16, line.product_id.categ_id and line.product_id.categ_id.display_name, normal_left)
				sheet1.write(row, 17, not x and sale.payment_term_id and sale.payment_term_id.name or "", normal_left)
				sheet1.write(row, 18, not x and sale.team_id and sale.team_id.name or "", normal_left)
				sheet1.write(row, 19, not x and sale.user_id and sale.user_id.name or "", normal_left)
				sheet1.write(row, 20, not x and states.get(sale.state, "") or "", normal_center)

				row += 1
				x += 1

				categ = line.product_id.categ_id
				if categ not in amt_per_categ:
					amt_per_categ[categ] = 0
				amt_per_categ[categ] += line.price_subtotal


		sheet2 = workbook.add_worksheet('Sheet2')
		sheet2.set_column(0, 0, 50)
		sheet2.set_column(1, 1, 25)
		row = 0
		sheet2.write(row, 0, "Product Category", header)
		sheet2.write(row, 1, "Sum of Subtotal", header)
		grand_total = 0
		row += 1
		for categ in amt_per_categ:
			grand_total += amt_per_categ.get(categ, 0)
			sheet2.write(row, 0, categ.display_name, normal_left)
			sheet2.write(row, 1, amt_per_categ.get(categ, 0), normal_number)
			row += 1
		sheet2.write(row, 0, "Grand Total", normal_left)
		sheet2.write(row, 1, grand_total, normal_number)
		row += 1

		chart = workbook.add_chart({
			'type': 'bar',
		})
		chart.add_series({
			'categories': '=Sheet2!$A$2:$A$%s' % str(row),
			'values': '=Sheet2!$B$2:$B$%s' % str(row)
		})
		chart.set_size({'width': 720, 'height': 500})
		sheet2.insert_chart('D1', chart)


		workbook.close()
		output = base64.encodestring(report.getvalue())
		report.close()

		view = self.env.ref('inno_sales_report.view_form_sale_order_report_wizard')
		wizard = self.env['sale.order.report.wizard'].create({
			'report': output,
			'name': filename,
			'is_download': True
		})

		return {
			'name': _('Download Report'),
			'type': 'ir.actions.act_window',
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'sale.order.report.wizard',
			'views': [(view.id, 'form')],
			'view_id': view.id,
			'target': 'new',
			'res_id': wizard.id,
		}
