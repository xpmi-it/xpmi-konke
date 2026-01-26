# -*- coding: utf-8 -*-
from odoo import _, api, fields, models


class ProductInherit(models.Model):
    _inherit = "product.product"

    qty_dropshipping = fields.Float(string='Quantity Drop', compute='compute_qty_drop')

    def compute_qty_drop(self):
        for product in self:
            qty_dropshipping = 0
            stock_line_id = self.env['connector.stock.line'].search(
                [('product_id', '=', product.id)], limit=1)
            if stock_line_id:
                qty_dropshipping = stock_line_id.qty_dropshipping
            product.qty_dropshipping = qty_dropshipping

    def force_update_stock_connector_line(self):
        model_connector_stock = self.env['connector.stock']
        model_connector_setting = self.env['connector.setting']
        model_connector_stock_line = self.env['connector.stock.line']
        for product in self:
            connector_stock_id = model_connector_stock.search([], limit=1)
            connector_stock_line_id = model_connector_stock_line.search([('product_id', '=', product.id)], limit=1)
            date_day_long_forecast_qty = model_connector_setting.get_date_day_long_forecast_qty()
            long_forecast_qty = model_connector_setting.get_long_forecast_qty(product,date_day_long_forecast_qty)
            connector_stock_line_vals = {'product_id': product.id,
                                         'connector_stock_id': connector_stock_id.id,
                                         'qty_available': product.qty_available,
                                         'virtual_available': product.virtual_available,
                                         'long_forecast_qty': long_forecast_qty,
                                         }
            if not connector_stock_line_id:
                model_connector_stock_line.create(connector_stock_line_vals)
            else:
                connector_stock_line_id.write(connector_stock_line_vals)


class ProductTemplateInherit(models.Model):
    _inherit = 'product.template'

    qty_dropshipping = fields.Float(string='Quantity Drop',
                                    inverse='_set_qty_drop',
                                    compute='_compute_qty_drop')

    @api.depends('product_variant_ids', 'product_variant_ids.qty_dropshipping')
    def _compute_qty_drop(self):
        unique_variants = self.filtered(
            lambda template: len(template.product_variant_ids) == 1)
        for template in unique_variants:
            template.qty_dropshipping = template.product_variant_ids.qty_dropshipping
        for template in (self - unique_variants):
            template.qty_dropshipping = ''

    def _set_qty_drop(self):
        if len(self.product_variant_ids) == 1:
            self.product_variant_ids.qty_dropshipping = self.qty_dropshipping
