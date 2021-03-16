# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)



class ShopFlow(models.Model):
    _name = 'shop_flow.shop_flow'
    _description = 'Shop Flow'

    name = fields.Char()
    order_id = fields.Many2one(comodel_name='sale.order', required=True)

    @api.model
    def connect_all_sale_orders(self):
        pass

    @api.model
    def get_all_sale_orders(self):
        return self.env['sale.order'].search([], order="id desc")

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    is_delivered = fields.Boolean(compute='_compute_delivered')
    # flow_record = fields.One2Many(comodel='shop_flow.shop_flow', inverse="order_id")

    def _compute_delivered(self):
        res = True
        for delivery in self.env['stock.picking'].search([('sale_id','=',self.id)],order="id desc"):
            for line in delivery.move_ids_without_package:
                if delivery.state != 'done':
                    res = False
        self.is_delivered = res

    @api.model
    def create(self, vals):
        res = super(SaleOrder, self).create(vals)
        self.env['shop_flow.shop_flow'].create({
            'order_id': res.id
        })
        _logger.info("\RESVAL: " + str(res) + "\n" + str(res.id))
        return res

class SaleLine(models.Model):
    _inherit = 'sale.order.line'

    def get_mo_records(self):
        mto = False
        for route in self.product_id.route_ids:
            if route.name == 'Replenish on Order (MTO)': # Default name for Odoo's MTO rule
                mto = True
                break
        if not mto:
            return self.product_id.get_mo_records()
        else:
            mrp_production_ids = self.order_id.procurement_group_id.stock_move_ids.created_production_id.procurement_group_id.mrp_production_ids.ids
            return mrp_production_ids

    def get_delivery_records(self):
        return self.env['stock.picking'].search([('sale_id','=',self.order_id.id)],order="id desc")

    def get_reserved(self):
        res = 0
        for deliveries in self.get_delivery_records():
            for delivery in deliveries.move_ids_without_package:
                if delivery.product_id == self.product_id and delivery.state == 'assigned':
                    res += delivery._compute_forecast_information() or delivery.forecast_availability
        return res

class Product(models.Model):
    _inherit = 'product.product'

    def get_mo_records(self):
        # self.route_ids
        return self.env['mrp.production'].search([('product_id','=',self.id),('state','in',['confirmed','progress','to_close'])],limit=80,order="id desc")

    def get_po_records(self):
        return self.env['purchase.order'].search([('order_line.product_id.id','=',self.id),('state','not in',['done','cancel'])])

class Production(models.Model):
    _inherit = 'mrp.production'

    def get_wo_records(self):
        return self.env['mrp.workorder'].search([('production_id','=',self.id)],limit=80)
    def get_product_lines(self):
        # Get product lines that match the bill of material and don't have an operation_id
        lines = []
        for move in self.move_raw_ids:
            for bom_line in self.bom_id.bom_line_ids:
                if bom_line.product_id == move.product_id:
                    if not bom_line.operation_id:
                        lines.append(move)
        return lines

class WorkOrder(models.Model):
    _inherit = 'mrp.workorder'

    def get_consumed_components(self):
        res = []
        products = []
        for p in self.check_ids:
            products.append(p.move_id.product_id)
        _logger.info("\nLENGTH: " + str(products))
        for line in self.production_id.move_raw_ids:
            _logger.info("\nCOMPARE: "+ str(line.product_id) + " IN " + str(products))
            if line.product_id in products:
                res.append(line)
        return res