# -*- coding: utf-8 -*-
# Copyright (C) 2023-Today:
#     Dinamiche Aziendali srl (<http://www.dinamicheaziendali.it/>)
# @author: Gianmarco Conte (gconte@dinamicheaziendali.it)
# License GPL-3.0 or later (http://www.gnu.org/licenses/gpl.html).
from odoo import fields, models


class ConnectorCarrier(models.Model):
    _name = 'connector.carrier'
    _rec_name = 'odoo_carrier_id'
    _description = 'Connector Carrier'

    name = fields.Char(string='Name', required=True)
    marketplace = fields.Selection([])
    odoo_carrier_id = fields.Many2one('delivery.carrier',
                                      string='Odoo Carrier',
                                      required=True)
