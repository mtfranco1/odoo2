from odoo import models, fields, api, _

class SaleOrderRMA(models.Model):
    _inherit = 'sale.order'

    repair_count = fields.Integer(compute='_compute_repairs')

    def _compute_repairs(self):
        self.repair_count =  self.env['rma.rma'].search_count([('sale_id', '=', self.id)])

    def get_repairs(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'RMAs',
            'view_mode': 'tree',
            'res_model': 'rma.rma',
            'domain': [('sale_id', '=', self.id)],
            'context': "{'create': False}"
        }