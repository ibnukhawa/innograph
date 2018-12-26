from odoo import api, fields, models
from odoo.exceptions import UserError

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    discount = fields.Monetary()
    amount = fields.Monetary(compute="_amount_disc_exclude")
    # invoice_line_ids = fields.One2many('account.invoice.line', 'invoice_id', string='Invoice Lines', oldname='invoice_line',
    #     readonly=True, states={'draft': [('readonly', False)]}, copy=True, domain=[('is_product_discount', '=', False)])

    @api.multi
    @api.depends('invoice_line_ids.price_subtotal')
    def _amount_disc_exclude(self):
        for invoice in self:
            amount = 0
            for line in invoice.invoice_line_ids:
                if not line.product_id.is_discount:
                    amount += line.price_subtotal
            invoice.amount = amount

    @api.model
    def create(self, vals):
        from_so = False
        discount = vals.get('discount')
        if not discount:
            if vals.get('type') == 'out_invoice' and vals.get('origin'):
                order = self.env['sale.order'].search([('name', '=', vals.get('origin'))])
                if order:
                    vals['discount'] = order.discount
                    from_so = True
        res = super(AccountInvoice, self.with_context(from_so=from_so)).create(vals)
        if res.type == 'out_invoice' and res.origin:
            res.compute_global_discount()
        return res

    @api.multi
    def write(self, vals):
        res = super(AccountInvoice, self).write(vals)
        for invoice in self:
            if invoice.type == 'out_invoice':
                from_so = self._context.get('from_so', False)
                invoice.compute_global_discount(from_so)
        return res

    def compute_global_discount(self, reverse=False):
        if self.discount < 0:
            raise UserError('Discount amount must be greater than 0, %s given' % self.discount)
        disc_line = False
        if reverse:
            invoice_line = self.invoice_line_ids.sorted(key=lambda r: r.id, reverse=True)
        else:
            invoice_line = self.invoice_line_ids
        for line in invoice_line:
            if line.product_id.is_discount:
                if disc_line:
                    line.unlink()
                else:
                    disc_line = line

        if self.discount == 0.0 and disc_line:
            disc_line.unlink()
        elif self.discount > 0.0:
            if disc_line:
                disc_line.quantity = 1
                disc_line.price_unit = - self.discount
                account_discount = False
                if disc_line and disc_line.account_analytic_id:
                    if disc_line.account_analytic_id.project_type_id:
                        project_type = disc_line.account_analytic_id.project_type_id
                        account_discount = project_type.discount_account_id
                
                if not account_discount:
                    account_discount = disc_line.product_id.property_account_income_id
                
                if account_discount:
                    disc_line.account_id = account_discount.id
            else:
                disc = self.env['product.product'].search([('is_discount', '=', True)], limit=1)
                if not disc:
                    raise UserError("No product identified as discount, please create one")
                else:
                    disc_account = disc.property_account_income_id or disc.categ_id.property_account_income_categ_id
                    if not disc_account:
                        raise UserError("No product discount account set, please set account for discount product")
                    disc_line = self.write({
                        'invoice_line_ids': [(0, False, {
                            'product_id': disc.id, 
                            'name': disc.name,
                            'uom_id': disc.uom_id.id,
                            'quantity': 1,
                            'price_unit': - self.discount,
                            'account_id': disc_account.id
                        })]
                    })
            
# class AccountInvoiceLine(models.Model):
#     _inherit = "account.invoice.line"

#     is_product_discount = fields.Boolean(related="product_id.is_discount")
