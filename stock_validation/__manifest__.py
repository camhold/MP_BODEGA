{
    'name': "Stock Validation",

    'summary': """Se valida la cantidad disponible en la ubicacion de destino""",

    'author': "Tonny Velazquez",
    'website': "corner.store59@gmail.com",

    'category': 'Stock',
    'version': '15.0.0.0.2',

    'depends': ['stock', 'stock_analytic', 'stock_request', 'mp_gestion', 'product',],

    'data': [
        'data/ir_cron_data.xml',
        'security/ir.model.access.csv',
        'views/stock_picking_views.xml',
        'views/stock_request_order_views.xml',
        'views/res_config_settings_views.xml',
        'views/location_report.xml',
        'wizard/stock_report_views_wizard.xml',
        'wizard/stock_location_report_wizard.xml',
    ],
}
