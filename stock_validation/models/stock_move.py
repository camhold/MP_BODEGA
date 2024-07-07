from odoo import api, fields, models
from odoo.exceptions import UserError


class StockMove(models.Model):
    _inherit = 'stock.move'

    qty_on_hand = fields.Float(compute='compute_qty_on_hand', string='Cantidad disponible')
    route_request_id = fields.Many2one(
        comodel_name='stock.location.route',
        string='Rutas',
        compute='_compute_route_request_ids'
    )

    product_standard_price = fields.Float(string='Costo estándar del producto', related='product_id.standard_price')
    product_single_standard_price = fields.Float(string='Costo unitario', related='product_id.standard_price')
    product_uom_total = fields.Float(string='Cantidad total de UM del producto', related='product_uom_qty')
    total_cost_id = fields.Monetary(string='Costo total', compute='_compute_total_cost',)
    currency_id = fields.Many2one('res.currency', string='Moneda', default=lambda self: self.env.user.company_id.currency_id)

    def _compute_route_request_ids(self):
        for move_id in self:
            print('dsmn')
            route_ids = self.env['stock.location.route']
            request_id = self.env['stock.request'].search([('name', '=', move_id.name)])
            move_id.route_request_id = request_id.route_id

    @api.model_create_multi
    def create(self, vals_list):
        res = super(StockMove, self).create(vals_list)
        res.onchange_move_ids_without_package()
        return res

    @api.onchange('product_id', 'location_id')
    def compute_qty_on_hand(self):
        for picking_id in self:
            if picking_id.state in ('cancel', 'done'):
                picking_id.qty_on_hand = picking_id.qty_on_hand
            else:
                if picking_id and picking_id.location_id and picking_id.product_id:
                    available_qty = self.env["stock.quant"].\
                        _get_available_quantity(picking_id.product_id, picking_id.location_id)
                    if picking_id.state == 'done':
                        picking_id.qty_on_hand = available_qty
                    else:
                        available_qty = self.env["stock.quant"].\
                            _get_available_quantity(picking_id.product_id, picking_id.location_id)
                        if picking_id.product_id and picking_id.location_id:
                            if available_qty <= 0:
                                picking_id.qty_on_hand = 0
                            elif available_qty == picking_id.quantity_done or available_qty <= picking_id.quantity_done:
                                picking_id.quantity_done = available_qty
                                picking_id.qty_on_hand = available_qty
                            else:
                                picking_id.qty_on_hand = available_qty
                        else:
                            picking_id.qty_on_hand = 0
                else:
                    picking_id.qty_on_hand = 0

    @api.onchange('analytic_account_id', 'analytic_tag_ids')
    def onchange_move_ids_without_package(self):
        for move_line_id in (self.picking_id.move_line_nosuggest_ids |
                             self.picking_id.move_line_ids_without_package |
                             self.picking_id.move_line_ids):
            if self.product_id == move_line_id.product_id:
                model_id = (move_line_id.id or move_line_id.id.origin)
                if model_id and self.analytic_account_id and self.analytic_tag_ids:
                    line_id = self.env['stock.move.line'].search([('id', '=', model_id)])
                    line_id.sudo().write({
                        "analytic_account_id": self.analytic_account_id.id,
                        "analytic_tag_ids": [(6, 0, self.analytic_tag_ids.ids)]
                    })

    @api.depends('product_standard_price', 'product_uom_total')
    def _compute_total_cost(self):
        for record in self:
            record.total_cost_id = record.product_standard_price * record.product_uom_total
