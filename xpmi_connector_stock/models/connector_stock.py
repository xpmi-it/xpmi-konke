# -*- coding: utf-8 -*-
# Copyright (C) 2023-Today:
#     Dinamiche Aziendali srl (<http://www.dinamicheaziendali.it/>)
# @author: Gianmarco Conte (gconte@dinamicheaziendali.it)
# License GPL-3.0 or later (http://www.gnu.org/licenses/gpl.html).
from odoo import fields, models, api


class ConnectorStock(models.Model):
    _name = 'connector.stock'
    _description = 'Connector Orders'

    date_update = fields.Datetime(string='Date Last Update')
    line_ids = fields.One2many('connector.stock.line', 'connector_stock_id',
                               string='Lines')


class ConnectorStockLine(models.Model):
    _name = 'connector.stock.line'
    _description = 'Connector Stock Line'
    _rec_name = 'product_id'

    connector_stock_id = fields.Many2one('connector.stock', string='Connector Stock',
                                         ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Product')
    qty_available = fields.Float(string='Qty Available')
    virtual_available = fields.Float(string='Expected Qty')
    qty_dropshipping = fields.Float(string='Dropshipping Qty')
    long_forecast_qty = fields.Float(string='Long Forecast Qty',
                                     help='You need to set in system parameters,'
                                          'if not set, default is 7 days')
    manual = fields.Boolean(string='Manual',
                            default=False)  # se cambio almeno una qty a mano, impostare a true
    active = fields.Boolean(string='Active', default=True)

    @api.onchange('qty_available', 'virtual_available', 'qty_dropshipping',
                  'long_forecast_qty')
    def _compute_manual(self):
        for line in self:
            line.manual = True

    def reset_qty_stock_line(self):
        model_connector_setting = self.env['connector.setting']
        for line in self:
            date_day_long_forecast_qty = model_connector_setting.get_date_day_long_forecast_qty()
            long_forecast_qty = model_connector_setting.get_long_forecast_qty(
                line.product_id,
                date_day_long_forecast_qty)
            conn_stock_line_vals = {'qty_available': line.product_id.qty_available,
                                    'virtual_available': line.product_id.virtual_available,
                                    'long_forecast_qty': long_forecast_qty,
                                    }
            line.write(conn_stock_line_vals)
            line.write({'manual': False})

    # non gestito componente che anche lui kit
    def compute_qty_available_product_kit(self, bom_id, exclude_location_ids):
        quant_model = self.env['stock.quant']
        product_qty = 9999999999
        for line in bom_id.bom_line_ids:
            quant_ids = quant_model.search([('location_id', 'in', exclude_location_ids.ids),
                                            ('product_id', '=', line.product_id.id)])
            qty_to_exclude = sum([x.quantity for x in quant_ids])
            component_qty = line.product_id.qty_available - qty_to_exclude
            product_qty_temp = int(component_qty / line.product_qty)  * bom_id.product_qty
            if product_qty_temp < product_qty:
                product_qty = product_qty_temp
        # se in diba la qty è più di 1, prendo il componente con qty inferiore
        # e moltiplicare per la qty della diba
        # if len(ratios_qty_available) == 0:
        #     ratios_qty_available.append(1)
        # return min(ratios_qty_available) * bom_id.product_qty   #TODO test, perchè lista vuota?
        return product_qty

    def get_qty_export(self, setting):
        type_calculation = setting.type_calculation
        quant_model = self.env['stock.quant']
        for line in self:
            quant_ids = quant_model.search(
                [('location_id', 'in', setting.exclude_location_ids.ids),
                 ('product_id', '=', line.product_id.id)])
            qty_to_exclude = sum([x.quantity for x in quant_ids])
            qty_available = line.qty_available
            bom_kit_ids = line.product_id.bom_ids.filtered(lambda diba: diba.type == 'phantom')
            bom_id = bom_kit_ids.filtered(lambda diba: diba.product_id.id == line.product_id.id)
            if not bom_id:
                bom_id = bom_kit_ids.filtered(lambda diba: not diba.product_id)
            final_qty = qty_available - qty_to_exclude
            if bom_id:
                final_qty = line.compute_qty_available_product_kit(bom_id[0], setting.exclude_location_ids)
            if type_calculation == 'qty_available':
                qty = final_qty
            elif type_calculation == 'virtual_available':
                qty = line.virtual_available - qty_to_exclude
            elif type_calculation == 'qty_dropshipping':
                qty = line.qty_dropshipping
            elif type_calculation == 'qty_available_and_qty_dropshipping':
                qty = final_qty + line.qty_dropshipping
            elif type_calculation == 'virtual_available_and_qty_dropshipping':
                qty = line.virtual_available + line.qty_dropshipping - qty_to_exclude
            elif type_calculation == 'virtual_available_and_qty_dropshipping_meno_long_forecast_qty':
                qty = line.virtual_available + line.qty_dropshipping - line.long_forecast_qty - qty_to_exclude
            elif type_calculation == 'virtual_available_meno_long_forecast_qty':
                qty = line.virtual_available - line.long_forecast_qty - qty_to_exclude
            return qty
