# -*- coding: utf-8 -*-

from odoo import models, fields, api
# import logging

# _logger = logging.getLogger(__name__)


class early_invoice(models.Model):
    _inherit = 'sale.order'

    has_invoice = fields.Boolean(compute="_has_invoice_compute", store=True)

    is_delivered = fields.Boolean(compute='_compute_delivered', store=True)

    @api.depends('delivery_count')
    def _compute_delivered(self):
        for record in self:
            res = True
            for delivery in record.env['stock.picking'].search([('sale_id','=',record.id)]):
                for line in delivery.move_ids_without_package:
                    if delivery.state != 'done':
                        res = False
                        break
            record.is_delivered = res

    # Only runs when invoice_ids changes
    # Will need some kickstart when app is installed to fill in values for pre-existing SO
    @api.depends('invoice_ids')
    def _has_invoice_compute(self):
        for record in self:
            record.has_invoice = len(record.invoice_ids.ids) > 0
            # _logger.info("\nLEN: "+str(len(record.invoice_ids.ids)))
