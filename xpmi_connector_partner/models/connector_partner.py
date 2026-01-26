# -*- coding: utf-8 -*-
# Copyright (C) 2023-Today:
# Dinamiche Aziendali srl (<http://www.dinamicheaziendali.it/>)
# @author: Giuseppe Borruso (gborruso@dinamicheaziendali.it)
# License GPL-3.0 or later (http://www.gnu.org/licenses/gpl.html).

from odoo import _, api, fields, models
from codicefiscale import isvalid
from odoo.exceptions import ValidationError

class ConnectorPartner(models.Model):
    _name = "connector.partner"
    _description = "Connector Partner"
    _rec_name = "partner_name"

    @api.model
    def _lang_get(self):
        return self.env["res.lang"].get_installed()

    partner_name = fields.Char(string="Name")
    # ref = fields.Char(string="Reference")
    vat = fields.Char(string="Vat")
    fiscalcode = fields.Char(string="Fiscal Code")
    street = fields.Char(string="Street")
    street2 = fields.Char(string="Street2")
    city = fields.Char(string="City")
    zip = fields.Char(string="Zip")
    state = fields.Char(string="State")
    state_id = fields.Many2one("res.country.state", string="State ID")
    country = fields.Char(string="Country")
    country_id = fields.Many2one("res.country", string="Country ID")
    phone = fields.Char(string="Phone")
    mobile = fields.Char(string="Mobile")
    email = fields.Char(string="Email")
    pec_mail = fields.Char(string="PEC")
    pec_destinatario = fields.Char(string="Addressee PEC")
    codice_destinatario = fields.Char(string="Addressee Code")
    comment = fields.Html(string="Notes")
    is_company = fields.Boolean(string="Is a Company")
    electronic_invoice_subjected = fields.Boolean(string="Subjected to Electronic Invoice")
    website = fields.Char(string="Website")
    # property_payment_term = fields.Char(string="Customer Payment Terms")
    # property_payment_term_id = fields.Many2one("account.payment.term", string="Customer Payment Terms ID")
    # property_supplier_payment_term = fields.Char(string="Vendor Payment Terms")
    # property_supplier_payment_term_id = fields.Many2one("account.payment.term", string="Vendor Payment Terms ID")
    # property_account_position = fields.Char(string="Fiscal Position")
    # property_account_position_id = fields.Many2one("account.fiscal.position", string="Fiscal Position ID")
    # property_account_payable = fields.Char(string="Account Payable")
    # property_account_payable_id = fields.Many2one("account.account", string="Account Payable ID")
    # property_account_receivable = fields.Char(string="Account Receivable")
    # property_account_receivable_id = fields.Many2one("account.account", string="Account Receivable ID")
    lang_char = fields.Char(string="Language")
    lang = fields.Selection(_lang_get, string="Language Odoo", default=None)
    bank_name = fields.Char(string="Bank Name")
    acc_number = fields.Char(string="Account Number")
    bank_id = fields.Many2one("res.bank", string="Bank")
    active = fields.Boolean(string="Active", default=True)
    done = fields.Boolean(string="Done", default=False)
    error = fields.Char(string="Error")
    partner_id = fields.Many2one('res.partner', string='Partner')

    def _search_partner(self):
        self.ensure_one()
        domain = []
        partner_id = False
        if self.partner_name:
            partner_name = " ".join(self.partner_name.split())
            domain = [("name", "=", partner_name)]
        if self.phone:
            domain.append(("phone", "=", self.phone)) #TODO se non c'è il phone o se diverso creo res.partner
        if domain:
            partner_id = self.env["res.partner"].search(domain)
        if not partner_id and self.vat and self.vat != "0":
            partner_id = self.env["res.partner"].search([("vat", "=", self.vat)])
        return partner_id

    def _search_state(self, state, country_id):
        model = self.env["res.country.state"]
        partner_import_model = self.env["connector.partner"]
        domain = [('code', '=', state)]
        if country_id:
            domain.append(('country_id', '=', country_id.id))
        state_id = model.search(domain, limit=1)
        if not state_id:
            domain = [('name', '=', state)]
            state_id = model.search(domain, limit=1)
        if not state_id:
            domain = [('name', 'ilike', state)]
            state_id = model.search(domain, limit=1)
        if not state_id:
            domain = [("state", "=", self.state),
                      ("state_id", '!=', False)]
            import_data = partner_import_model.search(domain, limit=1)
            state_id = import_data.state_id
            if not state_id:
                return False
        return state_id

    def _search_country(self, country):
        country_model = self.env["res.country"]
        partner_import_model = self.env["connector.partner"]
        domain = [("code", "=", country)]
        country_id = country_model.search(domain, limit=1)
        if not country_id:
            domain = [("name", "=", country)]
            country_id = country_model.search(domain, limit=1)
        if not country_id:
            domain = [("country", "=", country), ("country_id", "!=", False)]
            import_data = partner_import_model.search(domain, limit=1)
            country_id = import_data.country_id
            if not country_id:
                return False
        return country_id

    def import_res_partner_manually(self):
        self.import_res_partner(False)

    def prepare_partner_data(self):
        partner_data = {
            "name": self.partner_name,
            "company_type": "company" if self.is_company else "person",
            "vat": self.vat if self.vat else "",
            "street": self.street if self.street else "",
            "street2": self.street2 if self.street2 else "",
            "city": self.city if self.city else "",
            "zip": self.zip if self.zip else "",
            "state_id": self.state_id.id if self.state_id else "",
            "country_id": self.country_id.id if self.country_id else "",
            "phone": self.phone if self.phone else "",
            "lang": self.lang if self.lang else "",
            "mobile": self.mobile if self.mobile else "",
            "website": self.website if self.website else "",
            "email": self.email if self.email else "",
            "l10n_it_pec_email": (
                self.pec_mail
                if (
                    self.email
                    and "l10n_it_pec_email" in self.env["res.partner"].fields_get()
                )
                else ""
            ),
            "comment": self.comment if self.comment else "",
        }
        return partner_data

    def import_res_partner(self, connector_partner_id):
        if not connector_partner_id:
            connector_partner_ids = self.search([("done", "=", False)])
        else:
            connector_partner_ids = connector_partner_id
        partner_model = self.env["res.partner"]
        for import_data in connector_partner_ids:
            partner_data = import_data.prepare_partner_data()
            if not import_data.partner_id:
                if import_data.partner_name:
                    # search partner
                    partner_id = import_data._search_partner()
                    # create/write partner
                    if not partner_id:
                        partner_id = partner_model.create(partner_data)
                    else:
                        partner_id.write(partner_data)
                    if connector_partner_id.fiscalcode:
                        if partner_model._run_vat_test(connector_partner_id.fiscalcode, partner_id.country_id, partner_id.is_company):
                            partner_id.write({'vat': connector_partner_id.fiscalcode})
                        elif isvalid(connector_partner_id.fiscalcode):
                            partner_id.write({'fiscalcode': connector_partner_id.fiscalcode})
                        self.env.cr.commit()
                    import_data.partner_id = partner_id.id
                    import_data.done = True
                    self.env.cr.commit()
                else:
                    import_data.error = 'Partner Name Missing'
