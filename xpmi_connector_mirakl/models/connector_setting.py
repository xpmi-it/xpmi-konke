# -*- coding: utf-8 -*-
# Copyright (C) 2023-Today:
#     Dinamiche Aziendali srl (<http://www.dinamicheaziendali.it/>)
# @author: Gianmarco Conte (gconte@dinamicheaziendali.it)
# License GPL-3.0 or later (http://www.gnu.org/licenses/gpl.html).
from odoo import fields, models, api
import requests
import json
import csv
import io
import base64
import paramiko
from datetime import datetime, timedelta

header = ['gtin', 'stock']
header_pricelist = ['gtin', 'sku', 'selling_price',
                    'manufacturer_recommended_price', 'tax_rate_percentage']


class ConnectorSettingInherit(models.Model):
    _inherit = 'connector.setting'

    marketplace = fields.Selection(selection_add=[("mirakl", "Mirakl")])
    api_key = fields.Char(string='API Key')
    mapping_product_mirakl = fields.Selection([('sku', 'Sku')],
                                              string='Mapping Product Mirakl')
    mirakl_channel_codes = fields.Char(string='Mirakl Channel Codes')
    mirakl_shop_code = fields.Char(string='Mirakl Shop Code')
    mirakl_import_order_specific_channel = fields.Boolean(
        string='Import order specific channel',
        help='If you want to separate order for channel type, ex. '
             'LeroyMerlin IT, LeroyMerlin FR, etc, you must flag this field')
    mirakl_import_pricelist_stock_file = fields.Boolean(
        string='Import Pricelist and Stock file')
    use_shop_in_acceptance_call = fields.Boolean(string='Use Shop in Acceptance Call',
                                                 help='This is used in acceptance and in get data '
                                                      'customer after acceptance')

    def ir_cron_import_orders_mirakl(self):
        setting_ids = self.search([('marketplace', '=', 'mirakl'),
                                   ('import_order', '=', True)])
        for setting in setting_ids:
            setting.import_orders_mirakl()

    # def get_complete_url_import_order(self, url_import_order):
    #     for setting in self:
    #         if setting.limit_for_call:
    #             url_import_order += '&limit=' + str(setting.limit_for_call)
    #         url_import_order += '&orderStatusCodes=PENDING'
    #         if setting.privalia_import_shipped_order:
    #             url_import_order += ',SHIPPED'
    #         if setting.privalia_import_processing_order:
    #             url_import_order += ',PROCESSING'
    #         return url_import_order

    def get_complete_url_import_order_mirakl(self):
        url_import_order = self.url_import_order
        if self.range_import_order:
            now = datetime.now()
            start = now
            if self.range_import_order == 'since_yesterday':
                start = (now - timedelta(days=1))
            elif self.range_import_order == 'last_7_days':
                start = (now - timedelta(days=6))
            # url_import_order += '?start_date=' + str(start.date()) + '&end_date=' + str(end)
            url_import_order += '?start_date=' + str(start.date())
            # url_import_order += '?start_date=' + str(start.date())
            if self.limit_for_call:
                url_import_order += '&max=' + str(self.limit_for_call)
            if self.order_status_to_import:
                url_import_order += '&order_state_codes=' + self.order_status_to_import
            if self.mirakl_import_order_specific_channel and self.mirakl_channel_codes:
                url_import_order += '&channel_codes=' + self.mirakl_channel_codes
            if self.mirakl_shop_code:
                url_import_order += '&shop_id=' + self.mirakl_shop_code
        return url_import_order

    def import_orders_mirakl(self):
        model_connector_order = self.env['connector.order']
        model_connector_order_line = self.env['connector.order.lines']
        for setting in self:
            url_import_order = setting.get_complete_url_import_order_mirakl()
            headers = {
                'Content-Type': 'application/json',
                'Authorization': setting.api_key,
            }
            response = requests.request("GET", url_import_order, headers=headers)
            if response.status_code == 200:
                response_orders_json = json.loads(response.text)
                orders_json = response_orders_json['orders']
                if orders_json:
                    for order in orders_json:
                        existing_order_id = model_connector_order.search([('order_ref', '=', order['order_id'])])
                        if not existing_order_id:
                            order_vals = {}
                            if order['customer']:
                                connector_partner_id = setting.create_simple_partner(order)
                                order_vals['connector_partner_id'] = connector_partner_id.id
                                order_vals['connector_partner_shipping_id'] = connector_partner_id.id
                                order_vals['partner_shipping_id'] = connector_partner_id.partner_id.id
                                order_vals['partner_id'] = connector_partner_id.partner_id.id
                            order_vals['marketplace'] = 'mirakl'
                            order_vals['order_ref'] = order['order_id']
                            order_vals['marketplace_order_code'] = order['order_id']
                            order_vals['connector_state'] = order['order_state']
                            order_vals['create_order_date'] = order['created_date']
                            order_vals['update_order_date'] = order['last_updated_date']
                            order_vals['shipped_order_date'] = order['shipped_date'] if 'shipped_date' in order.keys() else ''
                            order_vals['amount_total'] = order['total_price']
                            order_vals['amount_shipping'] = order['shipping_price']
                            # order_vals['shipping_tax'] = order['shippingTaxRate']
                            order_vals['currency'] = order['currency_iso_code']
                            order_vals['currency_id'] = self.get_currency_id(order['currency_iso_code'])
                            order_vals['carrier_name'] = order['shipping_carrier_standard_code']
                            order_vals['tracking_number'] = order['shipping_tracking']
                            order_vals['tracking_url'] = order['shipping_tracking_url']
                            order_vals['connector_setting_id'] = setting.id
                            if 'channel' in order.keys() and type(order['channel']) == dict:
                                if 'label' in order['channel'].keys():
                                    order_vals['shop_channel_name'] = order['channel']['label']
                                if 'code' in order['channel'].keys():
                                    order_vals['shop_channel_id'] = order['channel']['code']
                            connector_order_id = model_connector_order.create(order_vals)
                            for line in order['order_lines']:
                                if len(line['taxes']) > 0 and 'rate' in line['taxes'][0].keys():
                                    vat_rate = int(line['taxes'][0]['rate']) if len(line['taxes']) > 0 else ''
                                else:
                                    vat_rate = 0
                                connector_line = model_connector_order_line.create(
                                    {'sku': line['offer_sku'],
                                     'description': line['product_title'],
                                     'price_unit': line['price_unit'],
                                     'vat_rate': vat_rate,
                                     'vat_included': True,
                                     'id_connector': line['order_line_id'],
                                     'quantity': line['quantity'],
                                     'connector_order_id': connector_order_id.id,
                                     'price_total': line['total_price']})
                                connector_line.set_product_id(setting,
                                                              setting.mapping_product_mirakl)
                            if not connector_order_id.partner_id or not connector_order_id.partner_shipping_id:
                                connector_order_id.state = 'ko'
                                connector_order_id.error_text = 'Partner or Partner Shipping missing'

    def create_simple_partner(self, order):#Only complete name and email for order not accepted
        partner_vals = {}
        res_partner_vals = {}
        connector_partner_model = self.env['connector.partner']
        res_partner_model = self.env['res.partner']
        complete_name = order['customer']['firstname'] + ' ' + order['customer']['lastname']
        partner_vals['partner_name'] = complete_name
        res_partner_vals['name'] = complete_name
        partner_vals['email'] = order['customer_notification_email']
        res_partner_vals['email'] = order['customer_notification_email']
        partner_id = res_partner_model.create(res_partner_vals)
        partner_vals['partner_id'] = partner_id.id
        connector_partner_id = connector_partner_model.create(partner_vals)
        return connector_partner_id

    def get_partner_shipping_vals_mirakl(self, order):
        partner_vals = {}
        complete_name = (order['customer']['shipping_address']['firstname']
                         + ' ' + order['customer']['shipping_address']['lastname'])
        domain = [('partner_name', '=', complete_name),
                  ('zip', '=', order['customer']['shipping_address']['zip_code'])]
        connector_partner_model = self.env['connector.partner']
        connector_partner_id = connector_partner_model.search(domain)
        if not connector_partner_id:
            partner_vals['partner_name'] = complete_name
            partner_vals['street'] = order['customer']['shipping_address']['street_1']
            partner_vals['street2'] = order['customer']['shipping_address']['street_2']
            partner_vals['city'] = order['customer']['shipping_address']['city']
            partner_vals['state'] = order['customer']['shipping_address']['state']
            partner_vals['zip'] = order['customer']['shipping_address']['zip_code']
            partner_vals['country'] = order['customer']['shipping_address']['country']
            if 'phone' in order['customer']['shipping_address'].keys():
                partner_vals['phone'] = order['customer']['shipping_address']['phone']
            partner_vals['email'] = order['customer_notification_email']
            partner_vals['lang'] = self.lang if self.lang else ""
            partner_vals['comment'] = order['customer']['shipping_address']['additional_info']
            connector_partner_id = connector_partner_model.create(partner_vals)
            self.set_data_on_connector_partner(connector_partner_id)
        return connector_partner_id

    def get_partner_billing_vals_mirakl(self, order):
        partner_vals = {}
        connector_partner_model = self.env['connector.partner']
        connector_partner_id = False
        if order['customer']['billing_address']:
            complete_name = order['customer']['billing_address']['firstname'] + ' ' + \
                            order['customer']['billing_address']['lastname']
            domain = [('partner_name', '=', complete_name),
                      ('zip', '=', order['customer']['billing_address']['zip_code'])]
            connector_partner_id = connector_partner_model.search(domain)
            if not connector_partner_id:
                if order['order_additional_fields']:
                    if order['order_additional_fields'][0]['code'] == 'administrative-tax-code' and order['order_additional_fields'][0]['value'] != '.':
                        partner_vals['fiscalcode'] = order['order_additional_fields'][0]['value']
                partner_vals['partner_name'] = complete_name
                partner_vals['street'] = order['customer']['billing_address']['street_1']
                partner_vals['street2'] = order['customer']['billing_address']['street_2']
                partner_vals['city'] = order['customer']['billing_address']['city']
                partner_vals['state'] = order['customer']['billing_address']['state']
                partner_vals['zip'] = order['customer']['billing_address']['zip_code']
                partner_vals['email'] = order['customer_notification_email']
                partner_vals['country'] = order['customer']['billing_address']['country']
                if 'phone' in order['customer']['shipping_address'].keys():
                    partner_vals['phone'] = order['customer']['shipping_address']['phone']
                partner_vals['lang'] = self.lang if self.lang else ""
        else:
            complete_name = order['customer']['firstname'] + ' ' + \
                            order['customer']['lastname']
            partner_vals['partner_name'] = complete_name
            partner_vals['email'] = order['customer_notification_email']
        if not connector_partner_id:
            connector_partner_id = connector_partner_model.create(partner_vals)
        self.set_data_on_connector_partner(connector_partner_id)
        return connector_partner_id

    def get_currency_id(self, currency):
        currency_model = self.env['res.currency']
        currency_id = currency_model.search([('name', '=', currency)], limit=1)
        if not currency_id:
            return False
        return currency_id.id

    def mirakl_get_carrier_info(self):
        model_connector_carrier_line = self.env['connector.carrier.line']
        for setting in self:
            if setting.url_carrier_info:
                url_import_order = setting.url_carrier_info
                payload = json.dumps({})
                headers = {
                    'Content-Type': 'application/json',
                    'Authorization': setting.api_key,
                }
                response = requests.request("GET", url_import_order, headers=headers, data=payload)
                if response.status_code == 200:
                    response_carrier_info_json = json.loads(response.text)
                    setting.write({'connector_carrier_line_ids': [(5)]})
                    for element in response_carrier_info_json['carriers']:
                        model_connector_carrier_line.create(
                            {
                                'connector_id': setting.id,
                                'carrier_code': element['code'],
                                'carrier_name': element['label'],
                                'standard_code': element['standard_code'] if 'standard_code' in element.keys() else "",
                                'tracking_url': element['tracking_url'],
                             })
                    return

    def ir_cron_send_file_pricelist_stock(self):
        domain = [('mirakl_import_pricelist_stock_file', '=', True)]
        setting_ids = self.env['connector.setting'].search(domain)
        if setting_ids:
            return