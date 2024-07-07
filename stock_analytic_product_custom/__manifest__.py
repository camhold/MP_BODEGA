# -*- coding: utf-8 -*-
{
    'name': "Stock Analytic Product Custom",
    'summary': "Analisis de inventario por producto",
    'author': "Adrian Hernandez",
    'website': "",
    'category': 'Stock',
    'version': '15.0.1.0.0',
    'depends': ['stock','product','account','analytic',],
    'data': [
        'security/ir.model.access.csv',
        'views/stock_analytic_product_views.xml',
    ],
}
