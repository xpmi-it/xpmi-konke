# -*- coding: utf-8 -*-
# Copyright (C) 2021-Today:
#     Dinamiche Aziendali srl (<http://www.dinamicheaziendali.it/>)
# @author: Gianmarco Conte (gconte@dinamicheaziendali.it)
# License GPL-3.0 or later (http://www.gnu.org/licenses/gpl.html).
from odoo import api, models


class WizardOrderImport(models.TransientModel):
    _name = 'wizard.order.import'
    _description = 'Wizard Order Import'

    def import_sale_order(self):
        model_connector_order = self.env['connector.order']
        connector_order_ids = model_connector_order.browse(self._context['active_ids'])
        model_connector_order.import_sale_order(connector_order_ids)
