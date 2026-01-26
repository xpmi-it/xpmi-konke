# -*- coding: utf-8 -*-
# Copyright (C) 2023-Today:
#     Dinamiche Aziendali srl (<http://www.dinamicheaziendali.it/>)
# @author: Gianmarco Conte (gconte@dinamicheaziendali.it)
# License GPL-3.0 or later (http://www.gnu.org/licenses/gpl.html).
from odoo import fields, models, api
from dateutil.relativedelta import relativedelta
from datetime import datetime

MAGIC_FIELDS = list(models.MAGIC_COLUMNS)
if hasattr(models.BaseModel, "CONCURRENCY_CHECK_FIELD"):
    MAGIC_FIELDS.append(models.BaseModel.CONCURRENCY_CHECK_FIELD)
else:
    MAGIC_FIELDS.append("__last_update")
domain_fields = """[("name", "not in", %s), ("ttype", "in", ["float", "integer"]), 
("model_id", "=", 'product.product'),]""" % str(MAGIC_FIELDS)


class ConnectorSettingInherit(models.Model):
    _inherit = 'connector.setting'

    # export_stock = fields.Boolean(string='Export Stock')
    exclude_location_ids = fields.Many2many('stock.location', string='Exclude Location',
                                            domain=[('usage', 'in', ['internal', 'transit'])])
    type_calculation = fields.Selection([
        ('qty_available', 'Qty Available'),
        ('virtual_available', 'Virtual Available'),
        ('qty_dropshipping', 'Qty Dropshipping'),
        ('qty_available_and_qty_dropshipping', 'Qty available+Dropshipping'),
        ('virtual_available_and_qty_dropshipping', 'Virtual Available+Dropshipping'),
        ('virtual_available_and_qty_dropshipping_meno_long_forecast_qty',
         'Virtual available+Drop-Long Forecast'),
        ('virtual_available_meno_long_forecast_qty', 'Virtual available-Long Forecast'),
    ], required=True, string='Type Calculation')

    send_stock = fields.Selection([('sftp', 'Sftp')],
                                  string='Send Stock')
    stock_user_sftp = fields.Char(string='Stock User Sftp')
    stock_pwd_sftp = fields.Char(string='Stock Pwd Sftp')
    stock_port_sftp = fields.Char(string='Stock Port Sftp')
    stock_ip_sftp = fields.Char(string='Url Sftp')
    stock_file_name = fields.Char(string='Filename Stock')
    stock_file_path_sftp = fields.Char(string='Path Sftp')
    stock_file = fields.Binary(string='Stock File', readonly=True,
                               help="File Stock",
                               copy=False)

    def ir_cron_export_stock(self):
        self.export_stock_product()

    def update_all_connector_stock_line(self):
        model_connector_stock = self.env['connector.stock']
        model_connector_stock_line = self.env['connector.stock.line']
        connector_stock_id = model_connector_stock.search([], limit=1)
        if not connector_stock_id:
            self.export_stock_product()
            return
        domain = [('detailed_type', 'in', ('product', 'consu'))]
        product_ids = self.env['product.product'].search(domain)
        connector_stock_line_ids = model_connector_stock_line.search([])
        date_day_long_forecast_qty = self.get_date_day_long_forecast_qty()
        for product in product_ids:
            long_forecast_qty = self.get_long_forecast_qty(product,
                                                           date_day_long_forecast_qty)
            connector_line_vals = {'product_id': product.id,
                                   'connector_stock_id': connector_stock_id.id,
                                   'qty_available': product.qty_available,
                                   'virtual_available': product.virtual_available,
                                   'long_forecast_qty': long_forecast_qty,
                                   }
            if product.id in connector_stock_line_ids.mapped('product_id').ids:
                line_ids = connector_stock_line_ids.filtered(lambda ctl: ctl.product_id.id == product.id)
                for line in line_ids:
                    if not line.manual:
                        if line.qty_available != product.qty_available or line.virtual_available != product.virtual_available or line.long_forecast_qty != long_forecast_qty:
                            line.write(connector_line_vals)
            else:
                model_connector_stock_line.create(connector_line_vals)
            connector_stock_id.write({'date_update': datetime.now()})

    def export_stock_product(self):
        model_connector_stock = self.env['connector.stock']
        model_connector_stock_line = self.env['connector.stock.line']
        # MRP is optional; guard BOM access when not installed.
        model_bom = self.env['mrp.bom'] if 'mrp.bom' in self.env else None
        connector_stock_id = model_connector_stock.search([], limit=1)
        domain = [('detailed_type', 'in', ('product', 'consu'))]
        product_ids = self.env['product.product'].search(domain)
        date_day_long_forecast_qty = self.get_date_day_long_forecast_qty()
        if not connector_stock_id:
            connector_stock_id = model_connector_stock.create({})
            product_stock_line_ids = []
            for product in product_ids:
                long_forecast_qty = self.get_long_forecast_qty(product, date_day_long_forecast_qty)
                product_stock_line_ids.append({'product_id': product.id,
                                               'connector_stock_id': connector_stock_id.id,
                                               'qty_available': product.qty_available,
                                               'virtual_available': product.virtual_available,
                                               'long_forecast_qty': long_forecast_qty,
                                               })
            if product_stock_line_ids:
                model_connector_stock_line.create(product_stock_line_ids)
            if product_ids:
                connector_stock_id.write({'date_update': datetime.now()})
        else:
            domain_move_line = [('date', '>=', connector_stock_id.date_update),
                                ('state', 'in',
                                 ('partially_available', 'assigned', 'done'))]
            move_line_ids = self.env['stock.move.line'].search(domain_move_line)
            product_ids = move_line_ids.mapped('product_id')
            product_to_update = move_line_ids.mapped('product_id')
            for product in product_ids:
                if model_bom and 'used_in_bom_count' in product._fields and product.used_in_bom_count > 0:
                    bom_from_prod_template_ids = model_bom.search([('bom_line_ids.product_id', '=', product.id)])
                    for bom in bom_from_prod_template_ids:
                        if bom.product_id:
                            product_to_update |= bom.product_id
                        else:
                            product_tmpl_id = bom.product_tmpl_id
                            for variant in product_tmpl_id.product_variant_ids:
                                product_to_update |= variant
            for product in product_to_update:
                conn_stock_line_id = model_connector_stock_line.with_context(active_test=False).search([('product_id', '=', product.id),
                                                                                                        ('connector_stock_id', '=', connector_stock_id.id)],
                                                                                                       limit=1) #TODO possono trovarne 2?
                conn_stock_line_vals = self.prepare_conn_stock_line_vals(product, date_day_long_forecast_qty)
                if conn_stock_line_id:
                    if conn_stock_line_id.active and not conn_stock_line_id.manual:
                        conn_stock_line_id.write(conn_stock_line_vals)
                    else:
                        continue
                else:
                    conn_stock_line_vals['product_id'] = product.id
                    model_connector_stock_line.create(conn_stock_line_vals)
            if product_ids:
                connector_stock_id.write({'date_update': datetime.now()})

    def prepare_conn_stock_line_vals(self, product, date_day_long_forecast_qty):
        long_forecast_qty = self.get_long_forecast_qty(product,
                                                       date_day_long_forecast_qty)
        conn_stock_line_vals = {'qty_available': product.qty_available,
                                'virtual_available': product.virtual_available,
                                'long_forecast_qty': long_forecast_qty,
                                }
        return conn_stock_line_vals

    def get_long_forecast_qty(self, product, date_day_long_forecast_qty):
        long_forecast_qty = 0
        move_line_ids = self.env['stock.move.line'].search(
            [('product_id', '=', product.id),
             ('picking_id.picking_type_id.code', '=', 'incoming'),
             ('move_id.purchase_line_id', '!=', False),
             ('state', 'not in', ('done', 'draft', 'cancel'))])
        for move in move_line_ids.filtered(
                lambda m: m.picking_id.scheduled_date > date_day_long_forecast_qty):
            long_forecast_qty += move.reserved_uom_qty
        return long_forecast_qty

    def get_qty_product(self, product, location_ids):
        domain = [('product_id', '=', product.id),
                  ('location_id', 'in', location_ids.ids)]
        product_quant_ids = self.env['stock.quant'].search(domain)
        qty = sum([x.quantity for x in product_quant_ids])
        return qty

    def get_date_day_long_forecast_qty(self):
        day_long_forecast_qty = int(
            self.env['ir.config_parameter'].sudo().get_param('day.for.long_forecast_qty'))
        if not day_long_forecast_qty:
            day_long_forecast_qty = 7
        date_day_long_forecast_qty = datetime.now() + relativedelta(
            days=day_long_forecast_qty)
        return date_day_long_forecast_qty
