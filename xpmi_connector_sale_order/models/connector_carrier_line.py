# -*- coding: utf-8 -*-
# Copyright (C) 2023-Today:
#     Dinamiche Aziendali srl (<http://www.dinamicheaziendali.it/>)
# @author: Gianmarco Conte (gconte@dinamicheaziendali.it)
# License GPL-3.0 or later (http://www.gnu.org/licenses/gpl.html).
from odoo import fields, models


class ConnectorCarrierLine(models.Model):
    _name = 'connector.carrier.line'

    carrier_code = fields.Char(string='Carrier Code')
    carrier_name = fields.Char(string='Carrier Name')
    standard_code = fields.Char(string='Standard Code')
    tracking_url = fields.Char(string='Tracking Url')
    connector_id = fields.Many2one('connector.setting', string='Connector Setting')
