# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.tools import float_is_zero


class mrp_fix(models.Model):
    _inherit = 'mrp.production'

    @api.depends(
        'move_raw_ids.state', 'move_raw_ids.quantity_done', 'move_finished_ids.state',
        'workorder_ids', 'workorder_ids.state', 'product_qty', 'qty_producing')
    def _compute_state(self):
        """ Compute the production state. It use the same process than stock
        picking. It exists 3 extra steps for production:
        - progress: At least one item is produced or consumed.
        - to_close: The quantity produced is greater than the quantity to
        produce and all work orders has been finished.
        """
        # TODO: duplicated code with stock_picking.py
        for production in self:
            if not production.move_raw_ids:
                production.state = 'draft'
            elif all(move.state == 'draft' for move in production.move_raw_ids):
                production.state = 'draft'
            elif all(move.state == 'cancel' for move in production.move_raw_ids):
                production.state = 'cancel'
            elif all(move.state in ('cancel', 'done') for move in production.move_raw_ids):
                production.state = 'done'
            elif production.qty_producing >= production.product_qty and all(wo.state in ['done','cancel'] for wo in production.workorder_ids):
                production.state = 'to_close'
            elif any(wo_state in ('progress', 'done') for wo_state in production.workorder_ids.mapped('state')):
                production.state = 'progress'
            elif not float_is_zero(production.qty_producing, precision_rounding=production.product_uom_id.rounding):
                production.state = 'progress'
            elif any(not float_is_zero(move.quantity_done, precision_rounding=move.product_uom.rounding or move.product_id.uom_id.rounding) for move in production.move_raw_ids):
                production.state = 'progress'
            else:
                production.state = 'confirmed'

            # Compute reservation state
            # State where the reservation does not matter.
            production.reservation_state = False
            # Compute reservation state according to its component's moves.
            if production.state not in ('draft', 'done', 'cancel'):
                relevant_move_state = production.move_raw_ids._get_relevant_state_among_moves()
                if relevant_move_state == 'partially_available':
                    if production.bom_id.operation_ids and production.bom_id.ready_to_produce == 'asap':
                        production.reservation_state = production._get_ready_to_produce_state()
                    else:
                        production.reservation_state = 'confirmed'
                elif relevant_move_state != 'draft':
                    production.reservation_state = relevant_move_state
