from odoo import models, sql_db
from datetime import date


class ResCurrency(models.Model):
    _inherit = "res.currency"

    def _cron_update_res_currency(self):
        db = sql_db.db_connect('PROCESOS')

        with db.cursor() as other_db_cursor:
            today = date.today()
            other_db_cursor.execute(
                'select valor, codigo_indicador from "INDICADORES_FINANCIEROS" WHERE fecha = ' + "'" +
                today.today().strftime("%Y-%m-%d") + "'"
            )

            result_db1 = other_db_cursor.fetchall()
            for result in result_db1:
                value = result[0]
                name = result[1].replace(' ', '').upper()
                if name == 'DOLAR':
                    name = 'USD'
                elif name == 'EURO':
                    name = 'EUR'
                clp_per_unit = 1 / value
                currency_id = self.env['res.currency'].search([('name', '=', name)])
                self.env["res.currency.rate"].create(
                    dict(currency_id=currency_id.id, name=today, rate=clp_per_unit)
                )
