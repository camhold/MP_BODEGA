from odoo import models, fields, api
from odoo.exceptions import UserError


class Picking(models.Model):
    _inherit = 'stock.picking'

    default_analytic_tag_ids = fields.Many2many(comodel_name="account.analytic.tag",
                                                string='Etiquetas Analiticas por defecto')
    default_analytic_account_id = fields.Many2one(comodel_name='account.analytic.account',
                                                  string='Cuenta analitica por default')

    def add_default_account_and_tag_analytic_account(self):
        for picking_id in self:
            for move_id in picking_id.move_ids_without_package:
                item_move_id = self.env['stock.move'].search([('id', '=', move_id.id)])
                # item_move_id.sudo().analytic_tag_ids = picking_id.default_analytic_tag_ids
                move_id.sudo().write({"analytic_tag_ids": picking_id.default_analytic_tag_ids.ids})
                move_id.sudo().analytic_account_id = picking_id.default_analytic_account_id
                move_id.sudo().invalidate_cache()
                move_id.sudo().onchange_move_ids_without_package()
    @api.model
    def create(self, vals):
        picking_id = super(Picking, self).create(vals)
        activity_type_id = self.env['mail.activity.type'].search([('id', '=', 4)])
        picking_id.activity_schedule(
            activity_type_id=activity_type_id.id,
            summary='test_summary',
            note='Note',
            user_id=picking_id.create_uid.id,
            date_deadline=picking_id.scheduled_date
        )
        return picking_id

    def button_validate(self):
        for move_id in self.move_ids_without_package:
            if not move_id.analytic_account_id or not move_id.analytic_tag_ids:
                raise UserError(f"El producto: {move_id.product_id.display_name}, "
                                f"no tiene cuenta analitica o no tiene etiqueta analitica "
                                f"en las operaciones")
        for move_line_id in self.move_line_nosuggest_ids:
            if not move_line_id.analytic_account_id or not move_line_id.analytic_tag_ids:
                raise UserError(f"El producto: {move_line_id.product_id.display_name}, "
                                f"no tiene cuenta analitica o no tiene etiqueta analitica "
                                f"en las operaciones detalladas")
        res = super(Picking, self).button_validate()
        move_ids = self.sudo().env['account.move'].search([('ref', 'ilike', f'{self.name}%')])
        account_id = self.sudo().env['account.analytic.account']
        tag_ids = self.sudo().env['account.analytic.tag']
        for move_id in move_ids:
            for line_id in move_id.line_ids:
                if line_id.sudo().analytic_account_id:
                    account_id = line_id.analytic_account_id
                if line_id.sudo().analytic_account_id:
                    tag_ids = line_id.analytic_tag_ids
            for line_id in move_id.line_ids:
                if account_id and tag_ids:
                    line_id.sudo().analytic_account_id = account_id
                    line_id.sudo().analytic_tag_ids = tag_ids
        return res

    def add_detailed_operation_analytic(self):
        for picking_id in self:
            for move_id in picking_id.move_ids_without_package:
                move_id.onchange_move_ids_without_package()

    def add_operation_analytic(self):
        for picking_id in self:
            for move_line_id in picking_id.move_line_ids_without_package:
                move_line_id.onchange_move_line_ids_without_package()

    def write(self, vals):
        if 'move_line_ids_without_package' in vals:
            for val in vals['move_line_ids_without_package']:
                if val[1]:
                    request_int_id = val[1]
                    if not isinstance(request_int_id, int) and 'virtual_' in val[1]:
                        request_int_id = request_int_id.split('_')[1]
                    move_line_id = self.env['stock.move.line'].search([('id', '=', request_int_id)], limit=1)
                    if move_line_id:
                        qty_done = move_line_id.qty_done
                        product_id = move_line_id.product_id
                        location_id = move_line_id.location_id
                        if val[2]:
                            if 'qty_done' in val[2]:
                                qty_done = val[2].get('qty_done')
                            if 'product_id' in val[2]:
                                product_id = self.env['product.product'].search([('id', '=', val[2].get('product_id'))])
                            if 'location_id' in val[2]:
                                location_id = self.env['stock.location'].search([('id', '=', val[2].get('location_id'))])
                            if qty_done != 0 and product_id and location_id:
                                available_qty = self.env["stock.quant"].\
                                    _get_available_quantity(product_id, location_id)
                                if available_qty <= 0:
                                    val[2]['qty_done'] = 0
                                elif available_qty == qty_done or available_qty <= qty_done:
                                    val[2]['qty_done'] = available_qty
        res = super(Picking, self).write(vals)
        # if self.location_id and self.location_dest_id and self.location_id == self.location_dest_id:
        #     raise UserError(f"No pueden ser las mismas ubicaciones de origen y destino")
        return res
