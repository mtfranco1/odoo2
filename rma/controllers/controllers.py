# -*- coding: utf-8 -*-
# from odoo import http


# class Rma(http.Controller):
#     @http.route('/rma/rma/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/rma/rma/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('rma.listing', {
#             'root': '/rma/rma',
#             'objects': http.request.env['rma.rma'].search([]),
#         })

#     @http.route('/rma/rma/objects/<model("rma.rma"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('rma.object', {
#             'object': obj
#         })
