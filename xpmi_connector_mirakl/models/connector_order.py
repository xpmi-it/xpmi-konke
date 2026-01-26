# -*- coding: utf-8 -*-
# Copyright (C) 2023-Today:
#     Dinamiche Aziendali srl (<http://www.dinamicheaziendali.it/>)
# @author: Gianmarco Conte (gconte@dinamicheaziendali.it)
# License GPL-3.0 or later (http://www.gnu.org/licenses/gpl.html).
from odoo import fields, models, api
import re
import requests
import json
from codicefiscale import isvalid


class ConnectorOrderInherit(models.Model):
    _inherit = 'connector.order'

    marketplace = fields.Selection(selection_add=[("mirakl", "Mirakl")])

    def ir_cron_update_order_status_mirakl(self):
        order_not_shipped = self.search([('connector_state', '=', "SHIPPING"),
                                         ('marketplace', '=', 'mirakl')])
        for connector_order in order_not_shipped.filtered(lambda order: order.sale_id):
            picking_ids = connector_order.sale_id.picking_ids.filtered(
                lambda so: so.state == 'done')
            if picking_ids:
                connector_order.mirakl_update_carrier_info_and_set_order_shipped(
                    picking_ids[0])

    def mirakl_update_carrier_info_and_set_order_shipped(self, picking_id):
        for order in self:
            if picking_id.carrier_tracking_ref and picking_id.url_tracking:
                setting = order.connector_setting_id
                url_update_order_status = setting.url_import_order + '/' + order.order_ref + '/tracking'
                if setting.mirakl_shop_code and setting.use_shop_in_acceptance_call:
                    url_update_order_status += '?shop_id=' + setting.mirakl_shop_code
                mirakl_carrier_id, mirakl_carrier_name = picking_id.get_mirakl_carrier()
                if not mirakl_carrier_name:
                    order.write({'error': True,
                                 'error_text': 'Missing Mirakl Carrier Information'})
                    continue
                if not mirakl_carrier_id:
                    mirakl_carrier_id = None
                payload_dict = {
                    "carrier_code": mirakl_carrier_id,
                    "carrier_name": mirakl_carrier_name,
                    "carrier_url": picking_id.url_tracking,
                    }
                if mirakl_carrier_id:
                    payload_dict.update({"tracking_number": picking_id.carrier_tracking_ref})
                payload = json.dumps(payload_dict)
                headers = {
                    'Content-Type': 'application/json',
                    'Authorization': setting.api_key,
                }
                order.call_update_carrier_info = 'url: ' + url_update_order_status + ' - headers: ' + str(
                    headers) + ' body: ' + str(payload)
                response = requests.request("PUT",
                                            url_update_order_status,
                                            headers=headers,
                                            data=payload)
                if response.status_code == 204:
                    url_validate_shipment = setting.url_import_order + '/' + order.order_ref + '/ship'
                    response_validate_ship = requests.request("PUT",
                                                              url_validate_shipment,
                                                              headers=headers,
                                                              data=json.dumps({}))
                    if response_validate_ship.status_code == 204:
                        order.write({'error': False,
                                     'error_text': '',
                                     'connector_state': 'SHIPPED',
                                     })
                    else:
                        order.write({'error': True,
                                     'error_text': response.text + ' ERROR VALIDATE SHIP',
                                     })
                else:
                    order.write({'error': True,
                                 'error_text': response.text + ' ERROR UPDATE CARRIER INFO',
                                 })
            else:
                order.write({'error': True,
                             'error_text': 'Missing tracking ref or url tracking'})

    def ir_cron_accept_order(self):
        order_not_accepted = self.search([('connector_state', '=', "WAITING_ACCEPTANCE"),
                                          ('marketplace', '=', 'mirakl'),
                                          ('sale_id', '!=', False)
                                          ])
        order_not_accepted = order_not_accepted.filtered(
            lambda co: co.sale_id.picking_ids)
        for order in order_not_accepted:
            picking_ids = order.sale_id.picking_ids.filtered(lambda pick: pick.state == 'assigned')
            if picking_ids:
                picking_ids[0].accept_order_mirakl()

    def get_complete_url_import_order_mirakl(self):
        for order in self:
            url_import_order = order.connector_setting_id.url_import_order + '?order_ids=' + order.order_ref
            return url_import_order

    def check_partner_regex_vat_fiscalcode(self, connector_setting_id,
                                           connector_partner_id, partner_id):
        if connector_setting_id.regex_vat:
            regex_vat = re.match(connector_setting_id.regex_vat,
                                 connector_partner_id.fiscalcode)
            if regex_vat:
                if regex_vat.group() == connector_partner_id.fiscalcode:
                    partner_id.write({'vat': connector_partner_id.fiscalcode})
        if connector_setting_id.regex_fiscalcode:
            regex_fiscalcode = re.search(connector_setting_id.regex_fiscalcode,
                                         connector_partner_id.fiscalcode)
            if regex_fiscalcode:
                if regex_fiscalcode.group() == connector_partner_id.fiscalcode:
                    partner_id.write({'fiscalcode': connector_partner_id.fiscalcode})

    def ir_cron_update_customer_info_after_acceptance(self):
        order_accepted = self.search([('connector_state', '=', "WAITING_DEBIT"),
                                      # TODO - forse add qui anche SHIPPING?
                                      ('marketplace', '=', 'mirakl'),
                                      ('sale_id', '!=', False)
                                      ])
        model_connector_partner = self.env['connector.partner']
        res_partner_model = self.env["res.partner"]
        for connector_order in order_accepted:
            connector_setting_id = connector_order.connector_setting_id
            url_import_order = connector_order.get_complete_url_import_order_mirakl()
            if connector_setting_id.mirakl_shop_code and connector_setting_id.use_shop_in_acceptance_call:
                url_import_order += '&shop_id=' + connector_setting_id.mirakl_shop_code
            headers = {
                'Content-Type': 'application/json',
                'Authorization': connector_setting_id.api_key,
            }
            connector_order.call_update_customer_info = 'url: ' + url_import_order + ' - headers: ' + str(
                headers)
            response = requests.request("GET", url_import_order, headers=headers)
            if response.status_code == 200:
                response_orders_json = json.loads(response.text)
                orders_json = response_orders_json['orders']
                for order in orders_json:
                    if order['order_id'] == connector_order.order_ref:
                        connector_partner_id = connector_order.connector_partner_id
                        connector_partner_ship_id = connector_order.connector_partner_shipping_id
                        if order['customer']['billing_address']:
                            partner_vals = {}
                            if order['order_additional_fields']:
                                if order['order_additional_fields'][0][
                                    'code'] == 'administrative-tax-code' and \
                                        order['order_additional_fields'][0][
                                            'value'] != '.':
                                    partner_vals['fiscalcode'] = \
                                    order['order_additional_fields'][0]['value']
                            partner_vals['partner_name'] = \
                            order['customer']['billing_address']['firstname'] + ' ' + \
                            order['customer']['billing_address']['lastname']
                            partner_vals['street'] = order['customer']['billing_address'][
                                'street_1']
                            partner_vals['street2'] = \
                            order['customer']['billing_address']['street_2']
                            partner_vals['city'] = order['customer']['billing_address'][
                                'city']
                            partner_vals['state'] = order['customer']['billing_address'][
                                'state']
                            partner_vals['zip'] = order['customer']['billing_address'][
                                'zip_code']
                            partner_vals['email'] = order['customer_notification_email']
                            partner_vals['country'] = \
                            order['customer']['billing_address']['country']
                            if 'phone' in order['customer']['shipping_address'].keys():
                                partner_vals['phone'] = \
                                order['customer']['shipping_address']['phone']
                            partner_vals[
                                'lang'] = connector_setting_id.lang if connector_setting_id.lang else ""
                            connector_partner_id.write(partner_vals)
                            connector_setting_id.set_data_on_connector_partner(
                                connector_partner_id)
                            partner_billing_data = connector_partner_id.prepare_partner_data()
                            partner_id = connector_partner_id.partner_id
                            partner_id.write(partner_billing_data)
                            if connector_partner_id.fiscalcode:
                                if not connector_setting_id.regex_vat and not connector_setting_id.regex_fiscalcode:
                                    if res_partner_model._run_vat_test(connector_partner_id.fiscalcode, partner_id.country_id, partner_id.is_company):
                                        partner_id.write({'vat': connector_partner_id.fiscalcode})
                                    elif isvalid(connector_partner_id.fiscalcode):
                                        partner_id.write({'fiscalcode': connector_partner_id.fiscalcode})
                                else:
                                    # connector_partner_id.fiscalcode -può essere sia codice fiscale che p.iva per mirakl
                                    connector_order.check_partner_regex_vat_fiscalcode(
                                        connector_setting_id, connector_partner_id,
                                        partner_id)
                        if order['customer']['shipping_address']:
                            partner_shipping_vals = {}
                            city = order['customer']['shipping_address']['city']
                            zip = order['customer']['shipping_address']['zip_code']
                            street = order['customer']['shipping_address']['street_1']
                            complete_name = (order['customer']['shipping_address'][
                                                 'firstname'] + ' ' +
                                             order['customer']['shipping_address'][
                                                 'lastname'])
                            if (complete_name != connector_partner_ship_id.partner_name
                                    or street != connector_partner_ship_id.street
                                    or city != connector_partner_ship_id.street
                                    or zip != connector_partner_ship_id.zip):
                                partner_shipping_vals['partner_name'] = complete_name
                                partner_shipping_vals['street'] = street
                                partner_shipping_vals['street2'] = \
                                order['customer']['shipping_address']['street_2']
                                partner_shipping_vals['city'] = city
                                partner_shipping_vals['state'] = \
                                order['customer']['shipping_address']['state']
                                partner_shipping_vals['zip'] = zip
                                partner_shipping_vals['country'] = \
                                order['customer']['shipping_address']['country']
                                if 'phone' in order['customer'][
                                    'shipping_address'].keys():
                                    partner_shipping_vals['phone'] = \
                                    order['customer']['shipping_address']['phone']
                                partner_shipping_vals['email'] = order[
                                    'customer_notification_email']
                                partner_shipping_vals[
                                    'lang'] = connector_setting_id.lang if connector_setting_id.lang else ""
                                partner_shipping_vals['comment'] = \
                                order['customer']['shipping_address']['additional_info']
                                connector_partner_shipping_id = model_connector_partner.create(
                                    partner_shipping_vals)
                                connector_setting_id.set_data_on_connector_partner(
                                    connector_partner_shipping_id)
                                partner_shipping_data = connector_partner_shipping_id.prepare_partner_data()
                                res_partner_shipping_id = res_partner_model.create(
                                    partner_shipping_data)
                                connector_partner_shipping_id.write(
                                    {'partner_id': res_partner_shipping_id.id})
                                connector_order.write(
                                    {
                                        'connector_partner_shipping_id': connector_partner_shipping_id.id,
                                        'partner_shipping_id': res_partner_shipping_id.id})
                                if connector_partner_shipping_id.fiscalcode:
                                    if not connector_setting_id.regex_vat and not connector_setting_id.regex_fiscalcode:
                                        if res_partner_model._run_vat_test(
                                                connector_partner_shipping_id.fiscalcode,
                                                res_partner_shipping_id.country_id,
                                                res_partner_shipping_id.is_company):
                                            res_partner_shipping_id.write({
                                                                              'vat': connector_partner_shipping_id.fiscalcode})
                                        elif isvalid(
                                                connector_partner_shipping_id.fiscalcode):
                                            res_partner_shipping_id.write({
                                                                              'fiscalcode': connector_partner_shipping_id.fiscalcode})
                                    else:
                                        connector_order.check_partner_regex_vat_fiscalcode(
                                            connector_setting_id, connector_partner_shipping_id,
                                            res_partner_shipping_id)
                                connector_order.sale_id.write(
                                    {'partner_shipping_id': res_partner_shipping_id.id})
                                connector_order.sale_id.picking_ids[0].write(
                                    {'partner_id': res_partner_shipping_id.id})
                            else:
                                connector_order.write(
                                    {
                                        'connector_partner_shipping_id': connector_order.connector_partner_id.id,
                                        'partner_shipping_id': connector_order.partner_id.id})
                        # se c'è street dello shipping address faccio questa write
                        # e metto order in spedizione
                        if order['customer']['shipping_address']['street_1']:
                            connector_order.write({'connector_state': 'SHIPPING'})
            else:
                connector_order.error_acceptance = response.text
        return order_accepted
