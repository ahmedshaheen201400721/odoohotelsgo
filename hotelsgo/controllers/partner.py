import json
import logging
import functools
import werkzeug.wrappers
from datetime import datetime, timedelta, date

from odoo import http
from odoo.addons.hotelsgo.models.common import invalid_response, valid_response, validate_token
from odoo.exceptions import AccessDenied, AccessError
from odoo.http import request

_logger = logging.getLogger(__name__)

class partner(http.Controller):

    @validate_token
    @http.route("/hotelsgo/booking", methods=["POST"], type="json", auth="public", csrf=False)
    def createPartnerAfterBooking(self, **kwargs):
        user_obj = request.env['res.users'].browse(request.session.uid)
        payload = request.httprequest.data.decode()
        payload = json.loads(payload)
        partner_obj = request.env['res.partner']
        email=payload.get("email")
        country=request.env['res.country'].sudo().search([ ('code','=',payload.get("country_code") )])
        country_id= country.id if country.id  else 192
        mailing_obj = request.env['mailing.contact']

        if not partner_obj.sudo().search([('email','=',email)]):
             partner_obj.with_user(user_obj).create({
                'name': " %s %s "%(payload.get("first_name"),payload.get("last_name")),
                'email': payload.get("email"),
                'phone': int(payload.get("phone")),
                'mobile': int(payload.get("phone")),
                'country_id':country_id
            })

        if not mailing_obj.sudo().search([('email','=',email)]):
             mailing_obj.with_user(user_obj).create({
                'name': " %s %s "%(payload.get("first_name"),payload.get("last_name")),
                'email': payload.get("email"),
                'list_ids': request.env['mailing.list'].browse(1),
                'country_id':country_id
             })

        return json.dumps({'status': 'booking'})

    @validate_token
    @http.route("/hotelsgo/signup", methods=["POST"], type="json", auth="public", csrf=False)
    def createPartnerAfterSignup(self, **kwargs):
        user_obj = request.env['res.users'].browse(request.session.uid)
        payload = request.httprequest.data.decode()
        payload = json.loads(payload)
        partner_obj = request.env['res.partner']
        email = payload.get("email")
        mailing_obj = request.env['mailing.contact']

        if not partner_obj.sudo().search([('email', '=', email)]):
            partner_obj.with_user(user_obj).create({
                'name': payload.get("name"),
                'email': payload.get("email"),
                'phone': payload.get("phone"),
                'mobile': payload.get("phone"),
            })

        if not mailing_obj.sudo().search([('email', '=', email)]):
            mailing_obj.with_user(user_obj).create({
                'name': payload.get("name"),
                'email': payload.get("email"),
                'list_ids': request.env['mailing.list'].browse(1),
            })

        return json.dumps({'status': 'success'})

    @validate_token
    @http.route("/hotelsgo/newsletter", methods=["POST"], type="json", auth="public", csrf=False)
    def createPartnerAfterNewsletter(self, **kwargs):
        user_obj = request.env['res.users'].browse(request.session.uid)
        payload = request.httprequest.data.decode()
        payload = json.loads(payload)
        email = payload.get("email")
        partner_obj = request.env['res.partner']
        mailing_obj = request.env['mailing.contact']

        if not partner_obj.sudo().search([('email', '=', email)]):
            partner_obj.with_user(user_obj).create({
                'name': payload.get("email"),
                'email': payload.get("email"),
            })

        if not mailing_obj.sudo().search([('email', '=', email)]):
            mailing_obj.with_user(user_obj).create({
                'name': payload.get("email"),
                'email': payload.get("email"),
                'list_ids': request.env['mailing.list'].browse(1),
            })

        return json.dumps({'status': 'success'})


