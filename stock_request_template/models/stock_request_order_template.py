from odoo import fields, models, api, _


class StockRequestOrderTemplate(models.Model):
    _name = "stock.request.order.template"
    _description = "Stock request template"

    name = fields.Char(string='Identificador', required=True)
    code = fields.Char(string='Codigo', default='/', copy=False, index=True,
                       readonly=True)
    description = fields.Text(string='Descripcion', required=True)
    company_id = fields.Many2one(
        "res.company",
        "Company",
        required=True,
        readonly=True,
        default=lambda self: self.env.company,
    )
    allow_virtual_location = fields.Boolean(
        related="company_id.stock_request_allow_virtual_loc", readonly=True
    )
    location_id = fields.Many2one(
        comodel_name="stock.location",
        string="Ubicacion",
        domain="not allow_virtual_location and "
        "[('usage', 'in', ['internal', 'transit'])] or []",
        ondelete="cascade",
        required=True,
    )
    warehouse_id = fields.Many2one(
        comodel_name="stock.warehouse",
        string="Almacen",
        check_company=True,
        readonly=False,
        ondelete="cascade",
        required=True,
    )
    default_analytic_tag_ids = fields.Many2many(comodel_name="account.analytic.tag",
                                                string='Etiquetas Analiticas por defecto')
    default_route_id = fields.Many2one(comodel_name='stock.location.route', string='Ruta por default')
    line_ids = fields.One2many(comodel_name='stock.request.order.template.line',
                               inverse_name='template_id', string='Lines')
    picking_policy = fields.Selection(
        [
            ("direct", "Receive each product when available"),
            ("one", "Receive all products at once"),
        ],
        string="Shipping Policy",
        required=True,
        default="direct",
    )
    analytic_account_id = fields.Many2one(
        comodel_name="account.analytic.account",
        string="Cuenta analitica por defecto",
        store=True,
        check_company=True,
        compute_sudo=True,
        required=True,
    )

    @api.model
    def create(self, vals):
        sequence = self.env['ir.sequence'].sudo().next_by_code('stock_request_order_template')
        if vals.get('code', '/') == '/':
            vals['code'] = sequence + " - " + vals['name']
        return super(StockRequestOrderTemplate, self).create(vals)

    @api.onchange("warehouse_id")
    def onchange_warehouse_id(self):
        if self.warehouse_id:
            # search with sudo because the user may not have permissions
            loc_wh = self.location_id.warehouse_id
            if self.warehouse_id != loc_wh:
                self.location_id = self.warehouse_id.lot_stock_id
                self.with_context(no_change_childs=True).onchange_location_id()
            if self.warehouse_id.company_id != self.company_id:
                self.company_id = self.warehouse_id.company_id
                self.with_context(no_change_childs=True).onchange_company_id()
        self.change_childs()

    def add_default_route(self):
        for order_id in self:
            for request_id in order_id.line_ids:
                request_id.sudo().route_id = order_id.default_route_id

    def add_default_account_and_tag_analytic_account(self):
        for order_id in self:
            for request_id in order_id.line_ids:
                request_id.sudo().write({"analytic_tag_ids": order_id.default_analytic_tag_ids.ids})
                request_id.sudo().analytic_account_id = order_id.analytic_account_id
                request_id.sudo().invalidate_cache()

    def change_childs(self):
        if not self._context.get("no_change_childs", False):
            for line in self.line_ids:
                line.warehouse_id = self.warehouse_id
                line.location_id = self.location_id
                line.company_id = self.company_id
                # line.picking_policy = self.picking_policy
                # line.expected_date = self.expected_date
                # line.requested_by = self.requested_by
                # line.procurement_group_id = self.procurement_group_id

    @api.onchange("location_id")
    def onchange_location_id(self):
        if self.location_id:
            loc_wh = self.location_id.warehouse_id
            if loc_wh and self.warehouse_id != loc_wh:
                self.warehouse_id = loc_wh
                self.with_context(no_change_childs=True).onchange_warehouse_id()
        self.change_childs()

