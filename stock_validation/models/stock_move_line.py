from odoo import models, fields, api
from odoo.exceptions import UserError


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    qty_on_hand = fields.Float(compute='compute_qty_on_hand', string='Cantidad disponible')
    analytic_tag_ids = fields.Many2many('account.analytic.tag', string='Etiquetas Analiticas',
                                        store=True, readonly=False, check_company=True, copy=True)

    product_standard_price = fields.Float(string='Costo estándar del producto', related='product_id.standard_price')
    product_single_standard_price = fields.Float(string='Costo unitario', related='product_id.standard_price')
    product_uom_total = fields.Float(string='Cantidad total de UM del producto', related='qty_done')
    total_cost_id = fields.Monetary(string='Costo total', compute='_compute_total_cost',)
    currency_id = fields.Many2one('res.currency', string='Moneda', default=lambda self: self.env.user.company_id.currency_id.id)


    @api.onchange('analytic_account_id', 'analytic_tag_ids')
    def onchange_move_line_ids_without_package(self):
        move_line_id = self
        for move_id in self.picking_id.move_ids_without_package:
            if move_id.product_id == move_line_id.product_id:
                model_id = (move_id.id or move_id.id.origin)
                if model_id:
                    move_id_id = self.env['stock.move'].search([('id', '=', model_id)])
                    move_id_id.sudo().write({
                        "analytic_account_id": self.analytic_account_id.id,
                        "analytic_tag_ids": [(6, 0, self.analytic_tag_ids.ids)]
                    })

    @api.model_create_multi
    def create(self, vals):
        for val in vals:
            if 'qty_done' in vals:
                qty_done = val['qty_done']
                product_id = self.env['product.product'].search([('id', '=', val['product_id'])])
                location_id = self.env['stock.location'].search([('id', '=', val['location_id'])])
                if qty_done != 0 and product_id and location_id:
                    available_qty = self.env["stock.quant"].\
                        _get_available_quantity(product_id, location_id)
                    if self._context.get('active_model') == 'stock.picking.type':
                        if available_qty <= 0:
                            val['qty_done'] = 0
                        elif available_qty == qty_done or available_qty <= qty_done:
                            val['qty_done'] = available_qty
        line_id = super(StockMoveLine, self).create(vals)
        for move_id in line_id.picking_id.move_ids_without_package:
            account_id = line_id.analytic_account_id or move_id.analytic_account_id
            tag_ids = line_id.analytic_tag_ids or move_id.analytic_tag_ids
            if line_id.product_id == move_id.product_id and account_id and tag_ids:
                line_id.sudo().write({
                    "analytic_account_id": account_id.id,
                    "analytic_tag_ids": [(6, 0, tag_ids.ids)]
                })
                move_id.sudo().write({
                    "analytic_account_id": account_id.id,
                    "analytic_tag_ids": [(6, 0, tag_ids.ids)]
                })
        return line_id

    @api.onchange('product_id', 'location_id')
    def compute_qty_on_hand(self):
        for picking_id in self:
            if picking_id and picking_id.product_id and picking_id.location_id:
                available_qty = self.env["stock.quant"].\
                    _get_available_quantity(picking_id.product_id, picking_id.location_id)
                if picking_id.state == 'done':
                    picking_id.qty_on_hand = available_qty
                else:
                    if picking_id:
                        if picking_id.product_id and picking_id.location_id:
                            if available_qty <= 0:
                                picking_id.qty_on_hand = 0
                            elif available_qty == picking_id.qty_done or available_qty <= picking_id.qty_done:
                                picking_id.qty_done = available_qty
                                picking_id.qty_on_hand = available_qty
                            else:
                                picking_id.qty_on_hand = available_qty
                        else:
                            picking_id.qty_on_hand = 0
                    else:
                        picking_id.qty_on_hand = 0
            else:
                picking_id.qty_on_hand = 0

    @api.depends('product_standard_price', 'product_uom_total')
    def _compute_total_cost(self):
        for record in self:
            record.total_cost_id = record.product_standard_price * record.product_uom_total