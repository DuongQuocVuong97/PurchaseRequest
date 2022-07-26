# -*- coding: utf-8 -*-
{
    'name': "purchase line",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr', 'stock', 'report_xlsx', 'purchase'],

    # always loaded
    'data': [
        'security/purchaseordered_security.xml',
        'security/ir.model.access.csv',
        'views/purchase_request_view.xml',
        'views/purchase_request_line_view.xml',
        'data/purchase_request_sequence.xml',
        'wizard/reject_reason_view.xml',
        'wizard/wizard_import_sale_order_line_view.xml',
        'wizard/purchase_xls.xml',
        'report/report_request_view.xml',
        'report/report_stat.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
