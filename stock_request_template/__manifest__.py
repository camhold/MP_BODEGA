{
    'name': "Stock Request Template",
    'summary': """Modulo para generar plantillas de solicitudes de existencia""",
    'author': "Tonny Velazquez",
    'website': "corner.store59@gmail.com",
    'category': 'Stock',
    'version': '15.0.0.0.1',
    'depends': ['stock_request'],
    'data': [
        'report/stock_request_order_report.xml',
        'data/stock_request_order_template_sequence_data.xml',
        'security/state_template_user.xml',
        'security/ir.model.access.csv',
        'views/stock_request_order_template_views.xml',
        'wizard/stock_order_template_wizard_views.xml',
    ],
}
