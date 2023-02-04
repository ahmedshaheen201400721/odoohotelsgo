import json
import logging
import functools
import werkzeug.wrappers
from datetime import datetime, timedelta, date

from odoo import http
from odoo.addons.hotelsgo.models.common import invalid_response, valid_response, validate_token
from odoo.exceptions import AccessDenied, AccessError
from odoo.http import request

class invoice(http.Controller):

    @http.route("/hotelsgo/invoice", methods=["POST"], type="json", auth="public", csrf=False)
    def createInvoiceBill(self, **post):
        user_obj = request.env['res.users'].browse(request.session.uid)
        # payload
        payload = request.httprequest.data.decode()
        payload = json.loads(payload)

        # prices
        tbo_price = float(payload.get("tbo_price"))
        final_price = float(payload.get("final_price"))

        # company
        company = self.get_record('res.company', 'HotelsGo.co')

        # sales_amount
        sales_amount = final_price * (float(company.sales_percentage)/100)
        gateway_amount = final_price - sales_amount - tbo_price

        # Partner
        partner_obj = request.env['res.partner']
        if not partner_obj.sudo().search([('email', '=', payload.get("email"))]):
            partner_obj.with_user(user_obj).create({
                'name': payload.get("email"),
                'email': payload.get("email"),
            })
        partner = partner_obj.sudo().search([('email', '=', payload.get("email"))], limit=1)

        # accounts
        TBOBank = self.get_record('account.account','TBOBank')
        TBO_expense = self.get_record('account.account','TBO_expense')
        hotelsgoBank = self.get_record('account.account','hotelsgoBank')
        hotelsgo_income = self.get_record('account.account','hotelsgo_income')

        # journals
        bill_journal = self.get_record('account.journal','bill_journal')
        invoice_journal = self.get_record('account.journal','invoice_journal')
        hotelsgoBank_journal = self.get_record('account.journal','hotelsgoBank_journal')
        TBOBank_journal = self.get_record('account.journal','TBOBank_journal')

        # products
        TBO_booking = self.get_record('product.template','TBO_booking')
        payment_Gateway = self.get_record('product.template','payment_Gateway')
        bill = self.create_bill(partner,TBO_booking, bill_journal, TBO_expense, payment_Gateway,TBOBank, TBOBank_journal, tbo_price, gateway_amount)
        invoice = self.create_invoice(partner,TBO_booking, hotelsgo_income, invoice_journal, hotelsgoBank,hotelsgoBank_journal,final_price)

        return json.dumps({'status': 'success'})

    def get_record(self,model,name):
        return request.env[model].sudo().search([('name', '=', name)])

    def create_bill(self,partner,TBO_booking, bill_journal, TBO_expense, payment_Gateway,TBOBank, TBOBank_journal,tbo_price, gateway_amount):
        total_bill=tbo_price + gateway_amount
        bill = request.env['account.move'].sudo().create({
            'partner_id': partner.id,
            'move_type': 'in_invoice',
            'invoice_date': date.today(),
            'date': date.today(),
            'journal_id': bill_journal.id,
            'line_ids': [
                (0, 0, {
                    'partner_id': partner.id,
                    'product_id': TBO_booking.id,
                    'name': "TBO bill",
                    "price_unit": tbo_price,
                    'debit': tbo_price,
                    'quantity': 1.0,
                    'tax_ids': None,
                    'account_id': TBO_expense.id,
                    'journal_id': bill_journal.id,
                    'exclude_from_invoice_tab': False,
                }),
                (0, 0, {
                    'partner_id': partner.id,
                    'product_id': payment_Gateway.id,
                    'name': "TBO bill",
                    "price_unit": gateway_amount,
                    'debit': gateway_amount,
                    'quantity': 1.0,
                    'tax_ids': None,
                    'account_id': TBO_expense.id,
                    'journal_id': bill_journal.id,
                    'exclude_from_invoice_tab': False,
                }),
                (0, 0, {
                    'name': "cash bill",
                    "price_unit": -total_bill,
                    'quantity': 1.0,
                    'tax_ids': None,
                    'account_id': TBOBank.id,  # 14
                    'journal_id':TBOBank_journal.id,
                    'exclude_from_invoice_tab': True,
                }),
            ]

        })

        bill.action_post()
        return bill

    def create_invoice(self, partner,TBO_booking, hotelsgo_income, invoice_journal, hotelsgoBank,hotelsgoBank_journal,final_price ):
        invoice = request.env['account.move'].sudo().create({
            'partner_id': partner.id,
            'move_type': 'out_invoice',
            'invoice_date': date.today(),
            'date': date.today(),
            'line_ids': [
                (0, 0, {
                    'partner_id': partner.id,
                    'product_id': TBO_booking.id,
                    'name': "TBO invoice",
                    "price_unit": final_price,
                    'credit': final_price,
                    'quantity': 1.0,
                    'tax_ids': None,
                    # 'move_id': invoice.id,
                    'account_id': hotelsgo_income.id,
                    'journal_id': invoice_journal.id,
                    'exclude_from_invoice_tab': False,
                }),
                (0, 0, {
                    'name': "cash invoice",
                    "price_unit": final_price,
                    'debit': final_price,
                    'quantity': 1.0,
                    'tax_ids': None,
                    'account_id': hotelsgoBank.id,  # 14
                    'journal_id':hotelsgoBank_journal.id,
                    'exclude_from_invoice_tab': True,
                }),
            ]

        })
        invoice.action_post()
        return invoice



