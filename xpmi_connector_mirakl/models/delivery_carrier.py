# -*- coding: utf-8 -*-
# Copyright (C) 2023-Today:
#     Dinamiche Aziendali srl (<http://www.dinamicheaziendali.it/>)
# @author: Gianmarco Conte (gconte@dinamicheaziendali.it)
# License GPL-3.0 or later (http://www.gnu.org/licenses/gpl.html).
from odoo import fields, models, api


class DeliveryCarrierInherit(models.Model):
    _inherit = 'delivery.carrier'

    mirakl_carrier_id = fields.Char(string='Mirakl Carrier ID')
    mirakl_carrier_name = fields.Char(string='Mirakl Carrier Name')
