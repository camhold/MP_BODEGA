from odoo import api, fields, models, tools


class IrUiMenu(models.Model):

    _inherit = "ir.ui.menu"

    readonly_purchase = fields.Boolean(compute="_compute_readonly_purchase")

    def _compute_readonly_purchase(self):
        user = self.env.user
        group_id = self.env.ref('purchase_manage_custom.group_purchase_user_purchase').id
        return user.has_group('purchase_manage_custom.group_purchase_user_purchase')
