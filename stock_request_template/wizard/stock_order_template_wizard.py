from odoo import models, fields


class StockOrderTemplateWizard(models.TransientModel):
    _name = 'stock.order.template.wizard'

    order_id = fields.Many2one(comodel_name='stock.request.order',
                               string='Solicitud')
    template_id = fields.Many2one(comodel_name='stock.request.order.template',
                                  string='Plantilla')

    name = fields.Char(related='template_id.name')
    code = fields.Char(related='template_id.code')
    description = fields.Text(related='template_id.description')

    def button_add_template(self):
        order_id = self.env['stock.request.order'].search([('id', '=', self.order_id.id)], limit=1)
        template_id = self.template_id
        order_id.default_route_id = template_id.default_route_id
        order_id.warehouse_id = template_id.warehouse_id
        order_id.location_id = template_id.location_id
        order_id.default_route_id = template_id.default_route_id.id,
        order_id.default_analytic_account_id = template_id.analytic_account_id
        order_id.default_analytic_tag_ids = template_id.default_analytic_tag_ids

        for line_id in template_id.line_ids:
            self.env['stock.request'].create({
                'warehouse_id': template_id.warehouse_id.id,
                'location_id': template_id.location_id.id,
                'order_id': order_id.id,
                'product_id': line_id.product_id.id,
                'product_uom_id': line_id.product_id.uom_id.id,
                'route_id': line_id.route_id.id,
                'analytic_tag_ids': [(6, 0, line_id.analytic_tag_ids.ids)],
                'product_uom_qty': line_id.product_uom_qty,
            })
