from odoo import api, fields, models, tools, _

class CurrencyRate(models.Model):
    _inherit = "res.currency.rate"

    rate = fields.Float(digits=(12, 12), default=1.0, help='The rate of the currency to the currency of rate 1')
