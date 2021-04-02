# -*- coding: utf-8 -*-
# from odoo import http


# class IotBugfix(http.Controller):
#     @http.route('/iot_bugfix/iot_bugfix/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/iot_bugfix/iot_bugfix/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('iot_bugfix.listing', {
#             'root': '/iot_bugfix/iot_bugfix',
#             'objects': http.request.env['iot_bugfix.iot_bugfix'].search([]),
#         })

#     @http.route('/iot_bugfix/iot_bugfix/objects/<model("iot_bugfix.iot_bugfix"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('iot_bugfix.object', {
#             'object': obj
#         })
