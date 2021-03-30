from odoo import models, fields, api, _

import logging

_logger = logging.getLogger(__name__)

class Return(models.TransientModel):
    _inherit ='stock.return.picking'

    def create_returns(self):
        for wizard in self:
            new_picking_id, pick_type_id = wizard._create_returns()
            if wizard.picking_id.picking_type_code == 'outgoing':
                for line in wizard.product_return_moves:
                    rma = self.env['rma.rma'].create({
                        'sale_id':wizard.picking_id.sale_id.id,
                        'product_id':line.product_id.id,
                        'location_id':wizard.location_id.id,
                        'product_uom':line.uom_id.id,
                        'partner_id':wizard.picking_id.sale_id.partner_id.id,
                        'product_qty':line.quantity,
                        'in_picking':new_picking_id,
                    })
        # Override the context to disable all the potential filters that could have been set previously
        ctx = dict(self.env.context)
        ctx.update({
            'search_default_picking_type_id': pick_type_id,
            'search_default_draft': False,
            'search_default_assigned': False,
            'search_default_confirmed': False,
            'search_default_ready': False,
            'search_default_planning_issues': False,
            'search_default_available': False,
        })
        return {
            'name': _('Returned Picking'),
            'view_mode': 'form,tree,calendar',
            'res_model': 'stock.picking',
            'res_id': new_picking_id,
            'type': 'ir.actions.act_window',
            'context': ctx,
        }