from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

import logging
_logger = logging.getLogger(__name__)

class MRP(models.Model):
    _inherit = 'mrp.production'

    rma_id = fields.Many2one('rma.rma', readonly=True)
    internal_notes = fields.Text('Internal Notes')


    def complete_rma(self):
        if self.state == 'done' and self.rma_id:
            if self.rma_id.invoice_method == 'after_repair':
                self.rma_id.state = '2binvoiced'
            else:
                self.rma_id.state = 'done'
            self.rma_id.ship_repair()

    def action_confirm(self):
        self._check_company()
        for production in self:
            if self.rma_id and self.rma_id.in_picking.state != 'done':
                raise UserError("The product to repair has not been recieved yet!")
            if production.bom_id:
                production.consumption = production.bom_id.consumption
            if not production.move_raw_ids:
                raise UserError(_("Add some materials to consume before marking this MO as to do."))
            # In case of Serial number tracking, force the UoM to the UoM of product
            if production.product_tracking == 'serial' and production.product_uom_id != production.product_id.uom_id:
                production.write({
                    'product_qty': production.product_uom_id._compute_quantity(production.product_qty, production.product_id.uom_id),
                    'product_uom_id': production.product_id.uom_id
                })
                for move_finish in production.move_finished_ids.filtered(lambda m: m.product_id == production.product_id):
                    move_finish.write({
                        'product_uom_qty': move_finish.product_uom._compute_quantity(move_finish.product_uom_qty, move_finish.product_id.uom_id),
                        'product_uom': move_finish.product_id.uom_id
                    })
            production.move_raw_ids._adjust_procure_method()
            (production.move_raw_ids | production.move_finished_ids)._action_confirm()
            production.workorder_ids._action_confirm()
            # run scheduler for moves forecasted to not have enough in stock
            production.move_raw_ids._trigger_scheduler()
        return True

    def button_mark_done(self):
        self._button_mark_done_sanity_checks()

        if not self.env.context.get('button_mark_done_production_ids'):
            self = self.with_context(button_mark_done_production_ids=self.ids)
        res = self._pre_button_mark_done()
        if res is not True:
            return res

        if self.env.context.get('mo_ids_to_backorder'):
            productions_to_backorder = self.browse(self.env.context['mo_ids_to_backorder'])
            productions_not_to_backorder = self - productions_to_backorder
        else:
            productions_not_to_backorder = self
            productions_to_backorder = self.env['mrp.production']

        self.workorder_ids.button_finish()

        productions_not_to_backorder._post_inventory(cancel_backorder=True)
        productions_to_backorder._post_inventory(cancel_backorder=False)
        backorders = productions_to_backorder._generate_backorder_productions()

        # if completed products make other confirmed/partially_available moves available, assign them
        done_move_finished_ids = (productions_to_backorder.move_finished_ids | productions_not_to_backorder.move_finished_ids).filtered(lambda m: m.state == 'done')
        done_move_finished_ids._trigger_assign()

        # Moves without quantity done are not posted => set them as done instead of canceling. In
        # case the user edits the MO later on and sets some consumed quantity on those, we do not
        # want the move lines to be canceled.
        (productions_not_to_backorder.move_raw_ids | productions_not_to_backorder.move_finished_ids).filtered(lambda x: x.state not in ('done', 'cancel')).write({
            'state': 'done',
            'product_uom_qty': 0.0,
        })

        for production in self:
            production.write({
                'date_finished': fields.Datetime.now(),
                'product_qty': production.qty_produced if not production.rma_id else production.rma_id.product_qty,
                'priority': '0',
                'is_locked': True,
            })
            production.complete_rma() # Validation checks are included in the method so no need to do them here

        for workorder in self.workorder_ids.filtered(lambda w: w.state not in ('done', 'cancel')):
            workorder.duration_expected = workorder._get_duration_expected()

        if not backorders:
            if self.env.context.get('from_workorder'):
                return {
                    'type': 'ir.actions.act_window',
                    'res_model': 'mrp.production',
                    'views': [[self.env.ref('mrp.mrp_production_form_view').id, 'form']],
                    'res_id': self.id,
                    'target': 'main',
                }
            return True
        context = self.env.context.copy()
        context = {k: v for k, v in context.items() if not k.startswith('default_')}
        for k, v in context.items():
            if k.startswith('skip_'):
                context[k] = False
        action = {
            'res_model': 'mrp.production',
            'type': 'ir.actions.act_window',
            'context': dict(context, mo_ids_to_backorder=None)
        }
        if len(backorders) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': backorders[0].id,
            })
        else:
            action.update({
                'name': _("Backorder MO"),
                'domain': [('id', 'in', backorders.ids)],
                'view_mode': 'tree,form',
            })
        return action