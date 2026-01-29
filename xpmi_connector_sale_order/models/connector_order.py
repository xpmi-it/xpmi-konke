# -*- coding: utf-8 -*-
# Copyright (C) 2023-Today:
#     Dinamiche Aziendali srl (<http://www.dinamicheaziendali.it/>)
# @author: Gianmarco Conte (gconte@dinamicheaziendali.it)
# License GPL-3.0 or later (http://www.gnu.org/licenses/gpl.html).
from odoo import fields, models, api
import requests


# from bs4 import BeautifulSoup
# from dateutil.parser import parse
# from datetime import datetime, timedelta
# from odoo.exceptions import UserError


class ConnectorOrder(models.Model):
    _name = 'connector.order'
    _description = 'Connector Orders'
    _rec_name = 'order_ref'

    marketplace = fields.Selection([])
    # *********************
    marketplace_name = fields.Char(string='Marketplace Name')
    marketplace_code = fields.Char(string='Marketplace Code')
    marketplace_order_code = fields.Char(string='Marketplace Order Code')
    shop_channel_id = fields.Char(string='Shop Channel Id')
    shop_channel_name = fields.Char(string='Shop Channel Name')
    create_order_date = fields.Char(string='Create Order Date')
    update_order_date = fields.Char(string='Update Order Date')
    shipped_order_date = fields.Char(string='Shipped Order Date')
    amount_total = fields.Monetary(string='Amount Total')
    amount_untaxed = fields.Monetary(string='Amount Untaxed')
    amount_shipping = fields.Monetary(string='Amount Shipping')
    shipping_tax = fields.Monetary(string='Amount Shipping')
    amount_tax = fields.Monetary(string='Amount Tax')
    currency = fields.Char(string='Currency')
    currency_id = fields.Many2one('res.currency', string='Currency ID')
    delivery_note_file = fields.Char(string='Delivery Note File')
    pickup_point_id = fields.Char(string='Pickup Point')

    refunded = fields.Boolean(string='Refunded')
    refund_date = fields.Char(string='Refund Date')
    refund_product_cost = fields.Char(string='Refund  Product Cost')
    # delivery information
    carrier_name = fields.Char(string='Carrier')
    tracking_number = fields.Char(string='Tracking Number')
    tracking_url = fields.Char(string='Tracking Url')
    # *********************

    connector_partner_id = fields.Many2one('connector.partner',
                                           string='Connector Partner')
    connector_partner_shipping_id = fields.Many2one('connector.partner',
                                                    string='Connector Partner Shipping')
    partner_id = fields.Many2one('res.partner', string='Partner')
    partner_shipping_id = fields.Many2one('res.partner', string='Partner Shipping')
    order_ref = fields.Char(string='Number')

    # state,currency ---da new table for mapping
    connector_state = fields.Char()
    state = fields.Selection([('ok', 'Ok'),
                              ('ko', 'Error')],
                             string='State',
                             compute='get_order_state',
                             store=True)
    # state = fields.Char(compute='_compute_state_field')
    sale_id = fields.Many2one('sale.order', string='Sale Order', readonly=True)
    error = fields.Boolean(string='Error')
    error_text = fields.Char(string='Error Text')
    imported = fields.Boolean(string='Imported')
    connector_setting_id = fields.Many2one('connector.setting', readonly=True,
                                           string='Connector Setting')
    order_line_ids = fields.One2many('connector.order.lines', 'connector_order_id',
                                     string='Order Lines')
    carrier_id = fields.Many2one('connector.carrier', string='Connector Carrier')

    call_acceptance = fields.Char(string='Call Acceptance')
    error_acceptance = fields.Char(string='Error Acceptance')
    call_update_customer_info = fields.Text(string='Call Update Customer Info')
    call_update_carrier_info = fields.Text(string='Call Update Carrier Info')

    @api.depends('partner_id', 'partner_shipping_id', 'order_line_ids',
                 'carrier_id', 'carrier_name')
    def get_order_state(self):
        for order in self:
            order.state = 'ok'
            if not order.partner_id or not order.partner_shipping_id or (
                    not order.carrier_id and order.carrier_name):
                order.state = 'ko'
                order.error_text = 'Partner or carrier missing'
                continue
            for line in order.order_line_ids:
                if not line.product_id:
                    order.state = 'ko'
                    order.error_text = 'Product not found'
                    continue



    def import_sale_order(self, order_ids=False):
        model_sale_order = self.env['sale.order']
        if not order_ids:
            order_ids = self
        for connector_order in order_ids:
            if connector_order.state == 'ok' and not connector_order.imported and not connector_order.sale_id:
                setting_id = connector_order.connector_setting_id
                sale_order_vals = connector_order.get_sale_order_vals(setting_id)
                existing_sale_id = model_sale_order.search(
                    [('name', '=', sale_order_vals['name'])])
                if not existing_sale_id:
                    sale_order_id = model_sale_order.create(sale_order_vals)
                    sale_order_line_ids = []
                    for line in connector_order.order_line_ids:
                        taxes_ids = connector_order.get_product_taxes(line,
                                                                      setting_id.get_tax_from_product)
                        if taxes_ids:
                            taxes_ids = taxes_ids.ids
                        sale_order_line_ids.append({'product_id': line.product_id.id,
                                                    'price_unit': line.price_unit,
                                                    'product_uom_qty': line.quantity,
                                                    'tax_id': [(6, 0, taxes_ids)],
                                                    'order_id': sale_order_id.id,
                                                    })
                    self.env['sale.order.line'].create(sale_order_line_ids)
                    carrier_id = connector_order.carrier_id.odoo_carrier_id
                    if not carrier_id:
                        carrier_id = setting_id.carrier_id
                    if carrier_id:
                        sale_order_id.set_delivery_line(carrier_id,
                                                        connector_order.amount_shipping)
                        sale_order_id.delivery_rating_success = True
                    sale_order_id._recompute_taxes()
                    if setting_id.automatic_confirm_sale_order:
                        sale_order_id.action_confirm()
                    connector_order.sale_id = sale_order_id.id
                    connector_order.imported = True

    def get_sale_order_vals(self, setting_id):
        for connector_order in self:
            sale_order_vals = {}
            if not setting_id.use_odoo_sequence:
                if setting_id.order_prefix:
                    sale_order_vals[
                        'name'] = setting_id.order_prefix + connector_order.marketplace_order_code
                else:
                    sale_order_vals['name'] = connector_order.marketplace_order_code
            sale_order_vals['partner_id'] = connector_order.partner_id.id
            sale_order_vals[
                'partner_shipping_id'] = connector_order.partner_shipping_id.id
            sale_order_vals['pricelist_id'] = setting_id.pricelist_id.id
            sale_order_vals['warehouse_id'] = setting_id.warehouse_id.id
            sale_order_vals['connector_order_id'] = connector_order.id
            sale_order_vals[
                'payment_term_id'] = setting_id.payment_term_id.id if setting_id.payment_term_id else False
            # if setting_id.fiscal_position_id:
            #     sale_order_vals['fiscal_position_id'] = setting_id.fiscal_position_id.id
            if setting_id.sale_order_team_id:
                sale_order_vals['team_id'] = setting_id.sale_order_team_id.id
            if connector_order.partner_id.vat:
                sale_order_vals['type_id'] = setting_id.sale_order_type_b2b_id.id
                sale_order_vals[
                    'fiscal_position_id'] = setting_id.fiscal_position_b2b_id.id
            else:
                sale_order_vals['type_id'] = setting_id.sale_order_type_b2c_id.id
                sale_order_vals['fiscal_position_id'] = setting_id.fiscal_position_id.id
            return sale_order_vals

    def get_product_taxes(self, line, get_tax_from_product):
        if get_tax_from_product:
            return line.product_id.taxes_id
        domain = [('amount', '=', line.vat_rate),
                  ('type_tax_use', '=', 'sale'),
                  ('country_id', '=', self.connector_setting_id.country_id.id)]
        if line.vat_included:
            domain.append(('price_include', '=', True))
        return self.env['account.tax'].search(domain, limit=1)


class ConnectorOrderLines(models.Model):
    _name = 'connector.order.lines'
    _description = 'Connector Order Lines'
    # _rec_name = 'order_ref'

    id_connector = fields.Char(strong='Id connector')
    connector_order_id = fields.Many2one('connector.order', string='Connector Order')
    product_id = fields.Many2one('product.product', string='Product')
    sku = fields.Char(string='Seller SKU')
    barcode = fields.Char(string='Barcode')
    description = fields.Char(string='Product description')
    brand = fields.Char(string='Brand')
    quantity = fields.Float(string='Quantity')
    quantity_refunded = fields.Float(string='Qty Refunded')
    price_unit = fields.Float(string='Price Unit')
    vat_included = fields.Boolean(string='Vat included')
    price_total = fields.Float(string='Price Total')
    vat_rate = fields.Char(string='VAT rate product')
    shipping_vat_rate = fields.Char(string='Vat rate shipping Fees')

    def set_product_id(self, setting, map_prod_marketplace):
        model_product = self.env['product.product']
        model_product_custumerinfo = self.env['product.customerinfo']
        mapping_product = self.connector_order_id.connector_setting_id.mapping_product.name
        for line in self:
            if map_prod_marketplace == 'sku':
                domain = [(mapping_product, '=', line.sku)]
                # if map_prod_marketplace == 'barcode':
                #     domain = [(mapping_product, '=', line.barcode)]
                product = model_product.search(domain, limit=1)
                if product:
                    line.product_id = product.id
                else:
                    domain = [('external_sku', '=', line.sku)]
                    product = model_product_custumerinfo.search(domain, limit=1)
                    if product:
                        line.product_id = product.product_id.id
