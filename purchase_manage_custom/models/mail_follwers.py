from odoo import api, fields, models
from odoo.exceptions import UserError


class Followers(models.Model):
    _inherit = 'mail.followers'

    def unlink(self):
        if self.user_has_groups("purchase_manage_custom.group_purchase_user_purchase")\
                and self.user_has_groups("purchase_manage_custom.group_purchase_manager"):
            raise UserError("No se puede eliminar registros.")
        return super(Followers, self).unlink()

    @api.model_create_multi
    def create(self, vals_list):
        records = super(Followers, self).create(vals_list)
        if self.user_has_groups("purchase_manage_custom.group_purchase_user_purchase")\
                and self.user_has_groups("purchase_manage_custom.group_purchase_manager"):
            raise UserError("No crear registros.")
        return records

    def write(self, vals):
        if self.user_has_groups("purchase_manage_custom.group_purchase_user_purchase")\
                and self.user_has_groups("purchase_manage_custom.group_purchase_manager"):
            raise UserError("No puede editar.")
        res = super(Followers, self).write(vals)
        return res
