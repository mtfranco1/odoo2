# -*- coding: utf-8 -*-
from odoo import http


class DeliveryScheduleManager(http.Controller):
    @http.route('/shop_flow/', auth='public')
    def index(self, **kw):
        return "Hello, world"

    @http.route('/shop_flow/objects/', auth='public')
    def list(self, **kw):
        return http.request.render('shop_flow.listing', {
            'root': '/shop_flow/shop_flow',
            'objects': http.request.env['sale.order'].search([]),
        })

    @http.route('/shop_flow/objects/<model("sale.order"):obj>/', auth='user')
    def object(self, obj, **kw):
        return http.request.render('shop_flow.object', {
            'object': obj
        })
    
    @http.route('/shop_flow/mo_data/<model("sale.order.line"):obj>/', auth='user')
    def mo_data(self, obj, **kw):
        data = obj.get_mo_records()
        po_data = obj.product_id.get_po_records()
        return http.request.render('shop_flow.mo_lines', {
            'objects': data,
            'po_data': po_data,
        })
    @http.route('/shop_flow/wo_data/<model("mrp.production"):obj>/', auth='user')
    def wo_data(self, obj, **kw):
        data = obj.get_wo_records()
        return http.request.render('shop_flow.wo_lines', {
            'objects': data,
        })
    @http.route('/shop_flow/mo_data_product/<model("product.product"):obj>/', auth='user')
    def mo_data_product(self, obj, **kw):
        data = obj.env['mrp.production'].search([('product_id','=',obj.id)],limit=80)
        po_data = obj.get_po_records()
        return http.request.render('shop_flow.mo_lines', {
            'objects': data,
            'po_data': po_data,
        })

    # @http.route('/shop_flow/po_data/<model("purchase.order.line"):obj>/', auth='user')
    # def mo_data_product(self, obj, **kw):
    #     data = obj.env['mrp.production'].search([('product_id','=',obj.id)],limit=80)
    #     po_data = obj.get_po_records()
    #     return http.request.render('shop_flow.mo_lines', {
    #         'objects': data,
    #         'po_data': po_data,
    #     })
