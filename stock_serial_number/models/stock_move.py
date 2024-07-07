import base64
import openpyxl
from io import BytesIO

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class StockMove(models.Model):
    _inherit = 'stock.move'

    attachment_name = fields.Char(string="Filename")
    attachment_file = fields.Binary(string="File")

    def btn_add_serial_number(self):
        return self._import_files()

    def _import_files(self, models=None):
        self._get_rows(self.attachment_file, self.attachment_name)

    def _get_rows(self, attachment, attachment_name):
        try:
            wb = openpyxl.load_workbook(filename=BytesIO(base64.b64decode(attachment)), read_only=True)
            ws = wb.active
            for record in ws.iter_rows(min_row=2, max_row=None, min_col=None,max_col=None, values_only=True):
                if self.product_id.name == record[2]:
                    lot_id = self.env['stock.production.lot'].search([
                        ('name', '=', record[0]),
                        ('product_id', '=', self.product_id.id)
                    ], limit=1)
                    if lot_id:
                        self.move_line_nosuggest_ids.create({
                            'location_dest_id': self.location_dest_id.id,
                            'product_uom_id': self.product_id.product_tmpl_id.uom_id.id,
                            'product_id': self.product_id.id,
                            'lot_id': lot_id.id,
                            'qty_done': 1,
                        })
        except Exception as e:
            raise ValidationError('Sintaxis de la plantilla incorrecto')
