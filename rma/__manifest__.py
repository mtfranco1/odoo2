# -*- coding: utf-8 -*-
{
    'name': "RMA",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "QOC Innovations",
    'website': "http://www.qocinnovations.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','mrp','sale','stock','sale_management','account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'report/rma_reports.xml',
        'views/mrp_views.xml',
        'views/insufficient_qty.xml',
        'report/repair_templates_repair_order.xml',
        'views/rma_data.xml',
        'views/account_move.xml',
        'views/sale.xml',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
