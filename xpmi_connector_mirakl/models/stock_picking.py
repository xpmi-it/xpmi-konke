# -*- coding: utf-8 -*-
# Copyright (C) 2023-Today:
#     Dinamiche Aziendali srl (<http://www.dinamicheaziendali.it/>)
# @author: Gianmarco Conte (gconte@dinamicheaziendali.it)
# License GPL-3.0 or later (http://www.gnu.org/licenses/gpl.html).
from odoo import fields, models, api
import requests, json


class StockPickingInherit(models.Model):
    _inherit = 'stock.picking'

    def get_mirakl_carrier(self):
        for picking in self:
            if picking.carrier_id and picking.carrier_id.mirakl_carrier_id and picking.carrier_id.mirakl_carrier_name:
                return picking.carrier_id.mirakl_carrier_id, picking.carrier_id.mirakl_carrier_name
            return False

    def accept_order_mirakl(self):
        for picking in self:
            connector_order_id = picking.sale_id.connector_order_id
            setting = connector_order_id.connector_setting_id
            if setting:
                if picking.state == 'assigned':
                    url_accept_order_status = setting.url_import_order + '/' + connector_order_id.order_ref + '/accept'
                    if setting.mirakl_shop_code and setting.use_shop_in_acceptance_call:
                        url_accept_order_status += '?shop_id=' + setting.mirakl_shop_code
                    payload = {"order_lines": []}
                    for line in connector_order_id.order_line_ids:
                        payload['order_lines'].append({"accepted": True, "id": line.id_connector})
                    headers = {'Content-Type': 'application/json',
                               'Authorization': setting.api_key}
                    payload = json.dumps(payload)
                    response = requests.request("PUT", url_accept_order_status,
                                                headers=headers, data=payload)
                    connector_order_id.call_acceptance = 'URL:' + url_accept_order_status + ' BODY: ' + str(payload)
                    if response.status_code == 204:
                        connector_order_id.write({'connector_state': 'WAITING_DEBIT',})
                    else:
                        connector_order_id.write(
                            {'error_text': 'Error in accept order:' + response.text,
                             'error_acceptance': response.text})
