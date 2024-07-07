from odoo import _, api, fields, models
from odoo.exceptions import UserError
from datetime import date, timedelta


class StockReportWizard(models.TransientModel):
    _name = "stock.report.wizard"
    _description = "Stock Report Wizard"

    date_report = fields.Date(string='Inventario a la fecha', required=True)

    def confirm_action(self):
        self = self.with_context(inventory_mode=True, create=False)
        first_day_current_month = self.date_report.replace(day=1)
        last_day_previous_month = first_day_current_month - timedelta(days=1)
        new_date = last_day_previous_month.replace(day=self.date_report.day) \
            if last_day_previous_month.day >= self.date_report.day else last_day_previous_month
        action = {
            'name': f'Informe analisis inventario: De la fecha'
                    f' {new_date.strftime("%d-%m-%Y")} a {self.date_report.strftime("%d-%m-%Y")}',
            'view_type': 'tree',
            'view_mode': 'list',
            'view_id': self.env.ref('stock.view_stock_quant_tree').id,
            'res_model': 'stock.quant',
            'type': 'ir.actions.act_window',
            'domain': [('in_date', '>=', new_date), ('in_date', '<=', self.date_report)],
            'context': {'create': False},
        }

        return action
