
from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    cancel_stock_request_automatic = fields.Boolean(
        string="Permitir cancelacion automatica de solicitudes de existencia y transferencias",
        readonly=False
    )

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            cancel_stock_request_automatic=self.env['ir.config_parameter'].sudo().get_param('cancel_stock_request_automatic', False)
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('cancel_stock_request_automatic', self.cancel_stock_request_automatic)
