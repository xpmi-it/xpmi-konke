# -*- coding: utf-8 -*-
# Copyright (C) 2023-Today:
# Dinamiche Aziendali srl (<http://www.dinamicheaziendali.it/>)
# @author: Giuseppe Borruso (gborruso@dinamicheaziendali.it)
# License GPL-3.0 or later (http://www.gnu.org/licenses/gpl.html).
from odoo import _, models, fields


class ConnectorSettingInherit(models.Model):
    _inherit = "connector.setting"

    def set_data_on_connector_partner(self, connector_partner_id):
        partner_vals = {}
        connector_partner_model = self.env['connector.partner']
        country_id = False
        if connector_partner_id.country_id:
            country_id = connector_partner_id.country_id
        if connector_partner_id.country and not connector_partner_id.country_id:
            country_id = connector_partner_model._search_country(connector_partner_id.country)
            if country_id:
                partner_vals['country_id'] = country_id.id
        if connector_partner_id.state and not connector_partner_id.state_id:
            state_id = connector_partner_model._search_state(connector_partner_id.state, country_id)
            if state_id:
                partner_vals['state_id'] = state_id.id
        connector_partner_id.write(partner_vals)

    regex_vat = fields.Char(string="Regular Expression for Vat")
    regex_fiscalcode = fields.Char(string="Regular Expression for Code")