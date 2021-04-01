# -*- coding: utf-8 -*-

from odoo import models, fields, api


class currency_bypass(models.Model):
    _inherit = 'res.currency'

    # Skip the error instructions defined in account>models>res_currency.py
    # Just call the default write function instead
    def write(self, vals):
        super(models.Model, self).write(vals)
