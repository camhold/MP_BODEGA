# -*- coding: utf-8 -*-

from odoo import models, fields, api

class StockMove(models.Model):
    _inherit ='stock.move'
    _description = 'Stock Analytic Product Custom'

    default_code = fields.Char(related='product_id.default_code', string='Referencia interna')
    product_name = fields.Char(related='product_id.name', string='nombre de producto')
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account')
    analytic_accounts_id = fields.Many2one(related='analytic_account_id', string='Cuenta analitica')
    analytic_tag_ids = fields.Many2many("account.analytic.tag", string="Analytic Tags")
