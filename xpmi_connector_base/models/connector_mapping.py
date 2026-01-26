# -*- coding: utf-8 -*-
# Copyright (C) 2023-Today:
#     Dinamiche Aziendali srl (<http://www.dinamicheaziendali.it/>)
# @author: Gianmarco Conte (gconte@dinamicheaziendali.it)
# License GPL-3.0 or later (http://www.gnu.org/licenses/gpl.html).
from odoo import fields, models, api


class ConnectorMapping(models.Model):
    _name = 'connector.mapping'
    _description = 'Connector Mapping'

    marketplace = fields.Selection([])
    field_type = fields.Selection([('state', 'State'),
                                   ('currency', 'Currency')],
                                  string='Field')
    marketplace_value = fields.Char(string='Marketplace Value', required=True)
    odoo_value = fields.Char(string='Odoo Value', required=True)
