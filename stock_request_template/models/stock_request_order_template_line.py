from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError
from odoo.tools import float_compare


class StockRequestOrderTemplateLine(models.Model):
    _name = "stock.request.order.template.line"
    _description = "Lines template"

    template_id = fields.Many2one(comodel_name='stock.request.order.template', string='Plantilla')
    description = fields.Text(string='Descripcion')
    company_id = fields.Many2one(
        "res.company",
        "Company",
        required=True,
        readonly=True,
        default=lambda self: self.env.company,
    )
    warehouse_id = fields.Many2one(related='template_id.warehouse_id', store=True)
    location_id = fields.Many2one(related='template_id.location_id', store=True)
    route_id = fields.Many2one(
        "stock.location.route",
        string="Route",
        domain="[('id', 'in', route_ids)]",
        ondelete="restrict",
    )

    analytic_account_id = fields.Many2one(
        comodel_name="account.analytic.account",
        string="Cuenta analitica",
    )
    route_ids = fields.Many2many(
        "stock.location.route",
        string="Routes",
        compute="_compute_route_ids",
        readonly=True,
    )

    product_uom_id = fields.Many2one(
        comodel_name="uom.uom",
        string="Product Unit of Measure",
    )
    product_id = fields.Many2one(
        "product.product",
        "Producto",
        ondelete="cascade",
        required=True,
    )
    analytic_tag_ids = fields.Many2many(comodel_name="account.analytic.tag",
                                        string='Etiquetas Analiticas por defecto')
    product_uom_qty = fields.Float(
        "Cantidad",
        required=True,
        default=1
    )

    @api.onchange("product_uom_qty")
    def onchange_product_uom_qty(self):
        if self.product_uom_qty <= 0:
            raise ValidationError('La cantidad del producto deberia de ser positivo')

    @api.onchange("location_id")
    def onchange_location_id(self):
        if self and self.template_id.location_id != self.location_id:
            raise ValidationError('La ubicación debe ser igual al pedido.')

    @api.depends("product_id", "warehouse_id", "location_id")
    @api.onchange("product_id", "warehouse_id", "location_id")
    def _compute_route_ids(self):
        route_obj = self.env["stock.location.route"]
        routes = route_obj.search(
            [("warehouse_ids", "in", self.mapped("warehouse_id").ids)]
        )
        routes_by_warehouse = {}
        for route in routes:
            for warehouse in route.warehouse_ids:
                routes_by_warehouse.setdefault(
                    warehouse.id, self.env["stock.location.route"]
                )
                routes_by_warehouse[warehouse.id] |= route
        for record in self:
            routes = route_obj
            if record.product_id:
                routes += record.product_id.mapped(
                    "route_ids"
                ) | record.product_id.mapped("categ_id").mapped("total_route_ids")
            if record.warehouse_id and routes_by_warehouse.get(record.warehouse_id.id):
                routes |= routes_by_warehouse[record.warehouse_id.id]
            parents = record.get_parents().ids
            record.route_ids = routes.filtered(
                lambda r: any(p.location_id.id in parents for p in r.rule_ids)
            )

    def get_parents(self):
        location = self.location_id
        result = location
        while location.location_id:
            location = location.location_id
            result |= location
        return result
