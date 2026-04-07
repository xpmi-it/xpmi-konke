# -*- coding: utf-8 -*-
# Copyright (C) 2021-Today:
#     Dinamiche Aziendali srl (<http://www.dinamicheaziendali.it/>)
# @author: Gianmarco Conte (gconte@dinamicheaziendali.it)
# License GPL-3.0 or later (http://www.gnu.org/licenses/gpl.html).
from odoo import api, models


class AcceptOrderMiraklWizard(models.TransientModel):
    _name = 'accept.order.mirakl.wizard'
    _description = 'Accept Orders Mirakl'

    def accept_orders_mirakl(self):
        model_picking = self.env['stock.picking']
        picking_ids = model_picking.browse(self._context['active_ids'])
        for picking in picking_ids:
            if picking.sale_id and picking.sale_id.connector_order_id.connector_setting_id:
                picking.accept_order_mirakl()
