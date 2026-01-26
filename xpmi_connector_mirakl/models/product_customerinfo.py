# -*- coding: utf-8 -*-
# Copyright (C) 2023-Today:
#     Dinamiche Aziendali srl (<http://www.dinamicheaziendali.it/>)
# @author: Gianmarco Conte (gconte@dinamicheaziendali.it)
# License GPL-3.0 or later (http://www.gnu.org/licenses/gpl.html).
from odoo import fields, models, api


class ProductCustomerinfoInherit(models.Model):
    _inherit = 'product.customerinfo'

    mirakl_product_id = fields.Char(string='Mirakl Product-id')
    marketplace = fields.Selection([], string='Marketplace',
                                   related='connector_setting_id.marketplace')
