from odoo import fields, models, api


class company(models.Model):
    _inherit = 'res.company'

    sales_percentage = fields.Float(string="Sales Percentage")
    payment_gateway_percentage = fields.Float(string="Payment Gateway Percentage")
