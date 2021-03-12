# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)



class qoc_sales_order_delivery_schedule(models.Model):
    _name = 'qoc.sales_order_delivery_schedule'
    _description = 'Sales Order Delivery Schedule'

    name = fields.Char()
    partner_id = fields.Many2one('res.partner')

class ResPartner(models.Model):
    _inherit = 'res.partner'

    def my_method(self):
        pass

class SaleLine(models.Model):
    _inherit = 'sale.order.line'

    def get_mo_records(self):
        return self.env['mrp.production'].search([('product_id','=',self.product_id.id),('state','in',['confirmed','progress','to_close'])],limit=80,order="id desc")
    def get_delivery_records(self):
        return self.env['stock.picking'].search([('sale_id','=',self.order_id.id)],limit=80,order="id desc")

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