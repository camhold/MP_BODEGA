from odoo import fields, models, api


class StockRequest(models.Model):
    _inherit = "stock.request"

    @api.depends("order_id")
    def _compute_analytic_tag_ids(self):
        """
        Set default analytic account on lines from order if defined.
        """
        for req in self:
            if req.order_id and req.order_id.analytic_tag_ids:
                req.analytic_tag_ids = req.order_id.default_analytic_tag_ids