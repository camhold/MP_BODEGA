{
    'name': "Action Cron Activities",

    'summary': """Se generan scripts con Odoo""",

    'author': "Tonny Velazquez",
    'website': "corner.store59@gmail.com",

    'category': 'Settings',
    'version': '15.0.0.0.1',

    'depends': ['base', 'web', 'purchase', 'sale'],

    'data': [
        'data/ir_cron_data.xml',
        'views/external_layout_standard.xml',
        'views/purchase_order_views.xml',
        'views/sale_order_views.xml',
    ],
}
