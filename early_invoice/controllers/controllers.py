# -*- coding: utf-8 -*-
# from odoo import http


# class EarlyInvoice(http.Controller):
#     @http.route('/early_invoice/early_invoice/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/early_invoice/early_invoice/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('early_invoice.listing', {
#             'root': '/early_invoice/early_invoice',
#             'objects': http.request.env['early_invoice.early_invoice'].search([]),
#         })

#     @http.route('/early_invoice/early_invoice/objects/<model("early_invoice.early_invoice"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('early_invoice.object', {
#             'object': obj
#         })
