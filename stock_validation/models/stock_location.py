from odoo import fields, models, api


class StockLocation(models.Model):
    _inherit = 'stock.location'

    in_date = fields.Datetime(compute='_compute_in_date', string='Fecha', store=True, compute_sudo=True)
    filter_init_date = fields.Datetime(string='Fecha filtrado inicial', default=False)
    filter_end_date = fields.Datetime(string='Fecha filtrado final', default=False)

    def get_history_moves(self):
        action = {
            'name': f'Hisotirial de movimientos',
            'view_type': 'tree',
            'view_mode': 'list',
            'view_id': self.env.ref('stock_validation.history_moves_tree_view').id,
            'res_model': 'stock.picking',
            'type': 'ir.actions.act_window',
            'domain': [
                ('location_dest_id', '=', self.id),
            ],
            'context': {'create': False},
        }
        return action

    @api.model
    def search_domain(self):
        domain = [
            ('complete_name', 'ilike', 'Holdc/stock%'),
        ]
        return domain

    def _compute_in_date(self):
        for location_id in self:
            picking_id = self.env['stock.picking'].search([
                '|',
                ('location_id', '=', location_id.id),
                ('location_dest_id', '=', location_id.id),
            ], order='create_date desc', limit=1)
            location_id.in_date = picking_id.create_date
