# -*- coding: utf-8 -*-
# Copyright (C) 2023-Today:
#     Dinamiche Aziendali srl (<http://www.dinamicheaziendali.it/>)
# @author: Gianmarco Conte (gconte@dinamicheaziendali.it)
# License GPL-3.0 or later (http://www.gnu.org/licenses/gpl.html).
from odoo import fields, models, api


class ProductCustomerinfoInherit(models.Model):
    _inherit = 'product.customerinfo'

    connector_setting_id = fields.Many2one('connector.setting', string='Connector')
    external_sku = fields.Char(string='External SKU')
    partner_id = fields.Many2one(string="Customer", help="Customer of this product",
                                 required=False)
