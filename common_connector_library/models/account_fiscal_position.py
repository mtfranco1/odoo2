# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.
import logging
from odoo import fields, models, api

_logger = logging.getLogger(__name__)

class AccountFiscalPosition(models.Model):
    _inherit = 'account.fiscal.position'

    origin_country_ept = fields.Many2one('res.country', string='Origin Country',
                                         help="Warehouse country based on sales order warehouse country system will "
                                              "apply fiscal position")

    @api.model
    def _get_fpos_by_region(self, country_id=False, state_id=False, zipcode=False, vat_required=False):
        """
        Inherited this method for selecting fiscal position based on warehouse (origin country).
        @param country_id:
        @param state_id:
        @param zipcode:
        @param vat_required:
        @return:
        """
        origin_country_id = self._context.get('origin_country_ept', False)
        if not origin_country_id:
            return super(AccountFiscalPosition, self)._get_fpos_by_region(country_id=country_id, state_id=state_id,
                                                                          zipcode=zipcode, vat_required=vat_required)
        return self.search_fiscal_position_based_on_origin_country(origin_country_id, vat_required)

    @api.model
    def search_fiscal_position_based_on_origin_country(self, origin_country_id, vat_required):
        """
        Search fiscal position based on origin country
        Updated by twinkalc on 11 sep 2020 - [changes related to the pass domain of company and is_amazon_fpos]
        """
        domain = [('auto_apply', '=', True), ('vat_required', '=', vat_required),
                  ('company_id', 'in', [self.env.company.id, False]), '|',
                  ('origin_country_ept', '=', origin_country_id), ('origin_country_ept', '=', False)]

        _logger.info(self.env.company.id)
        is_amazon_fpos = self._context.get('is_amazon_fpos', False)
        if is_amazon_fpos:
            domain.append(('is_amazon_fpos', '=', is_amazon_fpos))

        fiscal_position = self.search(domain + [('country_id', '=', origin_country_id)], limit=1)

        if not fiscal_position:
            fiscal_position = self.search(domain + [('country_group_id.country_ids', '=', origin_country_id)], limit=1)

        if not fiscal_position:
            fiscal_position = self.search(domain + [('country_id', '=', None), ('country_group_id', '=', None)],
                                          limit=1)
        return fiscal_position
