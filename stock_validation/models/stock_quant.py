from odoo import fields, models


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    default_code = fields.Char(related='product_id.default_code', string='Referencia interna')
    evaluation = fields.Float(compute='_compute_evaluation', string='Valorizacion')

    def _compute_evaluation(self):
        for quant_id in self:
            quant_id.evaluation = abs(quant_id.available_quantity * quant_id.product_id.standard_price)
