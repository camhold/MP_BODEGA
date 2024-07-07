from odoo import api, fields, models
from datetime import timedelta, datetime


class StockRequestOrder(models.Model):
    _inherit = "stock.request.order"

    order_template_wizard_ids = fields.One2many(comodel_name='stock.order.template.wizard',
                                                inverse_name='order_id')

    def action_report_stock_request_order(self):
        report = self.env.cr.dictfetchall()
        data = {'date': self.read()[0], 'report': report}
        return self.env.ref('stock_request_template.action_report_stock_request_form').report_action(None, data=data)

    def btn_use_template(self):
        view_id = self.env.ref('stock_request_template.template_order_wizard_tree')
        template_ids = self.env['stock.request.order.template'].search([])
        template_wizard_ids = self.env['stock.order.template.wizard']
        for template_id in template_ids:
            template_wizard_ids += self.env['stock.order.template.wizard'].create({
                'order_id': self.id,
                'template_id': template_id.id,
            })
        self.order_template_wizard_ids = template_wizard_ids
        return {
            'name': 'Selecciona tu plantilla',
            'view_mode': 'tree',
            'res_model': 'stock.order.template.wizard',
            'domain': [('order_id', '=', self.id)],
            'type': 'ir.actions.act_window',
            'target': 'new',
            'view_id': view_id.id,
            'flags': {'hasSelectors': False},
        }
