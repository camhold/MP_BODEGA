{
    'name': "Purchase Manage Custom",

    'summary': """Se agregan permisos adicionales al modelo de compras""",

    'author': "Tonny Velazquez",
    'website': "corner.store59@gmail.com",

    'category': 'purchase',
    'version': '15.0.0.0.1',

    'depends': ['base', 'purchase', 'purchase_requisition', 'stock'],

    'data': [
        'security/purchase_security.xml',
        'security/ir.model.access.csv',
        'views/menu_item_views.xml',
    ],
}
