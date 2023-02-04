# -*- coding: utf-8 -*-
# from odoo import http


# class Hotelsgo(http.Controller):
#     @http.route('/hotelsgo/hotelsgo', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/hotelsgo/hotelsgo/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('hotelsgo.listing', {
#             'root': '/hotelsgo/hotelsgo',
#             'objects': http.request.env['hotelsgo.hotelsgo'].search([]),
#         })

#     @http.route('/hotelsgo/hotelsgo/objects/<model("hotelsgo.hotelsgo"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('hotelsgo.object', {
#             'object': obj
#         })
