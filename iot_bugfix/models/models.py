# -*- coding: utf-8 -*-

from odoo import models, fields, api


class iot_bugfix(models.Model):
    _inherit = 'stock.picking'

    @api.returns('mail.message', lambda value: value.id)
    def message_post(self, **kwargs):
        message = super(models.Model, self).message_post(**kwargs)
        if message.attachment_ids and 'Label' in message.attachment_ids.mapped('name') and self.picking_type_id.iot_printer_id:
            self.env['bus.bus'].sendone(
                (self._cr.dbname, 'res.partner', self.env.user.partner_id.id),
                {
                    'type': 'iot_print_documents',
                    'documents': message.attachment_ids.mapped('datas'),
                    'iot_device_identifier': self.picking_type_id.iot_printer_id.identifier,
                    'iot_ip': self.picking_type_id.iot_printer_id.iot_ip,
                }
            )
        return message