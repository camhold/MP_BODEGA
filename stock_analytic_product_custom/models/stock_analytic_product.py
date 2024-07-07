# -*- coding: utf-8 -*-

from odoo import models, fields, api

class StockAnalyticProduct(models.Model):
    _name = 'stock.analytic.product.custom'
    _description = 'Stock Analytic Product Custom'

    product_product_id = fields.Many2one('product.product', required=True, string='Product')
    default_code = fields.Char(related='product_product_id.default_code', string='Default Code')
    product_name = fields.Char(related='product_product_id.name', string='Product Name')
    reference = fields.Char(compute='_compute_stock_data', string='Reference')
    product_qty = fields.Float(compute='_compute_stock_data', string='Product Quantity')
    qty_done = fields.Float(compute='_compute_stock_data', string='Quantity Done')
    scheduled_date = fields.Datetime(compute='_compute_stock_data', string='Scheduled Date')
    origin_location = fields.Many2one('stock.location', compute='_compute_stock_data', string='Origin Location')
    destination_location = fields.Many2one('stock.location', compute='_compute_stock_data', string='Destination Location')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting', 'Waiting'),
        ('confirmed', 'Confirmed'),
        ('assigned', 'Assigned'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')
    ], compute='_compute_stock_data', string='State')
    analytic_account = fields.Many2one('account.analytic.account', compute='_compute_stock_data', string='Analytic Account')

    @api.depends('product_product_id')
    def _compute_stock_data(self):
        for record in self:
            record.reference = ''
            record.product_qty = 0
            record.qty_done = 0
            record.scheduled_date = False
            record.origin_location = False
            record.destination_location = False
            record.state = ''
            record.analytic_account = False


            stock_move_lines = self.env['stock.move.line'].search([('product_id', '=', record.product_product_id.id)], limit=1)
            if stock_move_lines:
                stock_move_line = stock_move_lines[0]
                record.reference = stock_move_line.reference
                record.product_qty = stock_move_line.product_uom_qty
                record.qty_done = stock_move_line.qty_done
                picking = stock_move_line.picking_id
                if picking:
                    record.scheduled_date = picking.scheduled_date
                    record.origin_location = picking.location_id.id
                    record.destination_location = picking.location_dest_id.id
                    record.state = picking.state
                    record.analytic_account = picking.default_analytic_account_id.id