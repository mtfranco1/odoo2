from odoo import api, SUPERUSER_ID
# import logging

# _logger = logging.getLogger(__name__)

def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    records = env['sale.order'].search([])
    records._compute_delivered()
    records._has_invoice_compute()
    # _logger.info("\nHOOK RAN")