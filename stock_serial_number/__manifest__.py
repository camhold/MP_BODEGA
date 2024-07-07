{
    'name': "Stock Numeros de Serie",

    'summary': """Se agrega la carga masiva para numeros de serie desde las operaciones detalladas en el picking""",
    'author': "Tonny Velazquez",
    'website': "erp.holdconet.com",

    'category': 'stock',
    'version': '15.0.0.0.1',

    'depends': ['stock'],

    'data': [
        'views/stock_move_views.xml',
    ],
}
