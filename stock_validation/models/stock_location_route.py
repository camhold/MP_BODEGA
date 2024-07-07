from odoo import _, api, models, fields
from odoo.exceptions import ValidationError


class StockLocationRoute(models.Model):
    _inherit = "stock.location.route"

    move_request_id = fields.Many2one(comodel_name='stock.move', string='Movimiento')
