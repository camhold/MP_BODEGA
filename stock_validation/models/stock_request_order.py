from odoo import api, fields, models
from datetime import timedelta, datetime


class StockRequestOrder(models.Model):
    _inherit = "stock.request.order"

    default_analytic_tag_ids = fields.Many2many(comodel_name="account.analytic.tag",
                                                string='Etiquetas Analiticas por defecto')
    default_route_id = fields.Many2one(comodel_name='stock.location.route', string='Ruta por default')

    def add_default_route(self):
        for order_id in self:
            for request_id in order_id.stock_request_ids:
                request_id.sudo().route_id = order_id.default_route_id


    def add_default_account_and_tag_analytic_account(self):
        for order_id in self:
            for request_id in order_id.stock_request_ids:
                item_request_id = self.env['stock.request'].search([('id', '=', request_id.id)])
                # item_request_id.sudo().analytic_tag_ids = order_id.default_analytic_tag_ids
                request_id.sudo().write({"analytic_tag_ids": order_id.default_analytic_tag_ids.ids})
                request_id.sudo().analytic_account_id = order_id.default_analytic_account_id
                request_id.sudo().invalidate_cache()

    def _cron_update_terminate_records(self):
        order_ids = self.env['stock.request.order'].search([])
        cancel_automatic = self.env['ir.config_parameter'].sudo().get_param('cancel_stock_request_automatic') or False
        for order_id in order_ids:
            date_end = order_id.expected_date + timedelta(days=4)
            if datetime.now() > date_end and order_id.state != 'done' and cancel_automatic:
                order_id.action_cancel()

    @api.model
    def create(self, vals):
        order_id = super(StockRequestOrder, self).create(vals)
        activity_type_id = self.env['mail.activity.type'].search([('id', '=', 4)])
        order_id.activity_schedule(
            activity_type_id=activity_type_id.id,
            summary='test_summary',
            note='Note',
            user_id=order_id.create_uid.id,
            date_deadline=order_id.expected_date
        )
        return order_id
