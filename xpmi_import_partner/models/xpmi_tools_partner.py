# Copyright (C) 2023-Today:
# Dinamiche Aziendali srl (<http://www.dinamicheaziendali.it/>)
# @author: Giuseppe Borruso (gborruso@dinamicheaziendali.it)
# License GPL-3.0 or later (http://www.gnu.org/licenses/gpl.html).

from odoo import _, api, fields, models


@api.model
def _lang_get(self):
    return self.env["res.lang"].get_installed()


class XpmiToolsPartnerImport(models.Model):
    _name = "xpmi_tools.partner_import"
    _description = "Partner Import"
    _rec_name = "partner_name"

    partner_name = fields.Char(string="Name")
    ref = fields.Char(string="Reference")
    vat = fields.Char(string="Tax ID")
    fiscalcode = fields.Char(string="Codice Fiscale")
    street = fields.Char()
    street2 = fields.Char()
    city = fields.Char()
    zip = fields.Char()
    state = fields.Char()
    state_id = fields.Many2one("res.country.state", string="State ID")
    country = fields.Char()
    country_id = fields.Many2one("res.country", string="Country ID")
    phone = fields.Char()
    mobile = fields.Char()
    fax = fields.Char()
    email = fields.Char()
    pec_mail = fields.Char(string="PEC e-mail")
    codice_destinatario = fields.Char(string="Destination Code")
    comment = fields.Html(string="Notes")
    is_company = fields.Boolean(string="Is a Company", default=True)
    electronic_invoice_subjected = fields.Boolean(
        string="Subjected to Electronic Invoice", default=True
    )
    website = fields.Char()
    property_payment_term = fields.Char(string="Customer Payment Terms")
    property_payment_term_id = fields.Many2one(
        "account.payment.term", string="Customer Payment Terms ID"
    )
    property_supplier_payment_term = fields.Char(string="Vendor Payment Terms")
    property_supplier_payment_term_id = fields.Many2one(
        "account.payment.term", string="Vendor Payment Terms ID"
    )
    property_account_position = fields.Char(string="Fiscal Position")
    property_account_position_id = fields.Many2one(
        "account.fiscal.position", string="Fiscal Position ID"
    )
    property_account_payable = fields.Char(string="Account Payable")
    property_account_payable_id = fields.Many2one(
        "account.account", string="Account Payable ID"
    )
    property_account_receivable = fields.Char(string="Account Receivable")
    property_account_receivable_id = fields.Many2one(
        "account.account", string="Account Receivable ID"
    )
    lang_char = fields.Char(string="Language")
    lang = fields.Selection(_lang_get, string="Language Odoo", default=None)
    bank_name = fields.Char()
    acc_number = fields.Char(string="Account Number")
    bank_id = fields.Many2one("res.bank", string="Bank")
    active = fields.Boolean(default=True)
    done = fields.Boolean(default=False)
    error = fields.Char()

    @api.model
    def _skip_compute_state(self):
        """Hook for skip compute state"""
        return False

    def _check_consistency(self):
        self.ensure_one()
        self.error = ""

        if not self.partner_name:
            self.error = _("Missing name")
            return False
        if not self.country and not self.country_id and self.state:
            self.error = _("Set country if state is set")
            return False
        return True

    def _search_partner(self):
        self.ensure_one()

        partner_id = self.env["res.partner"]
        if self.ref:
            partner_id = self.env["res.partner"].search([("ref", "=", self.ref)])
        if not partner_id and self.vat and self.vat != "0":
            partner_id = self.env["res.partner"].search([("vat", "=", self.vat)])
        return partner_id

    def _default_data(self):
        self.ensure_one()

        data = {
            "state_id": self.state_id or self.env["res.country.state"],
            "country_id": self.country_id or self.env["res.country"],
            "property_payment_term_id": (
                self.property_payment_term_id or self.env["account.payment.term"]
            ),
            "property_supplier_payment_term_id": (
                self.property_supplier_payment_term_id
                or self.env["account.payment.term"]
            ),
            "property_account_position_id": (
                self.property_account_position_id or self.env["account.fiscal.position"]
            ),
            "bank_id": self.bank_id or self.env["res.bank"],
            "property_account_receivable_id": (
                self.property_account_receivable_id or self.env["account.account"]
            ),
            "property_account_payable_id": (
                self.property_account_payable_id or self.env["account.account"]
            ),
            "lang": self.lang,
        }
        return data

    def _search_country(self):
        self.ensure_one()

        domain = [("name", "=", self.country)]
        country_id = self.env["res.country"].search(domain, limit=1)
        if country_id:
            return country_id

        domain = [("country", "=", self.country), ("country_id", "!=", False)]
        import_data = self.search(domain, limit=1)
        return import_data.country_id if import_data.country_id else False

    def _search_state(self, country_id):
        self.ensure_one()

        domain = [
            "|",
            ("name", "=", self.state),
            ("code", "=", self.state),
            ("country_id", "=", country_id),
        ]
        state_id = self.env["res.country.state"].search(domain, limit=1)
        if state_id:
            return state_id

        domain = [
            ("state", "=", self.state),
            ("country_id", "=", country_id),
            ("state_id", "!=", False),
        ]
        import_data = self.search(domain, limit=1)
        return import_data.state_id if import_data.state_id else False

    def _search_property_payment_term(self):
        self.ensure_one()

        domain = [("name", "=", self.property_payment_term)]
        property_payment_term_id = self.env["account.payment.term"].search(
            domain, limit=1
        )
        if property_payment_term_id:
            return property_payment_term_id

        domain = [
            ("property_payment_term", "=", self.property_payment_term),
            ("property_payment_term_id", "!=", False),
        ]
        import_data = self.search(domain, limit=1)
        return (
            import_data.property_payment_term_id
            if import_data.property_payment_term_id
            else False
        )

    def _search_property_supplier_payment_term(self):
        self.ensure_one()
        supplier_payment_term = self.property_supplier_payment_term

        domain = [("name", "=", supplier_payment_term)]
        property_supplier_payment_term_id = self.env["account.payment.term"].search(
            domain, limit=1
        )
        if property_supplier_payment_term_id:
            return property_supplier_payment_term_id

        domain = [
            ("property_supplier_payment_term", "=", supplier_payment_term),
            ("property_supplier_payment_term_id", "!=", False),
        ]
        import_data = self.search(domain, limit=1)
        return (
            import_data.property_supplier_payment_term_id
            if import_data.property_supplier_payment_term_id
            else False
        )

    def _search_property_account_payable(self):
        self.ensure_one()
        account_payable = self.property_account_payable

        domain = ["|", ("code", "=", account_payable), ("name", "=", account_payable)]
        property_account_payable_id = self.env["account.account"].search(
            domain, limit=1
        )
        if property_account_payable_id:
            return property_account_payable_id

        domain = [
            ("property_account_payable", "=", account_payable),
            ("property_account_payable_id", "!=", False),
        ]
        import_data = self.search(domain, limit=1)
        return (
            import_data.property_account_payable_id
            if import_data.property_account_payable_id
            else False
        )

    def _search_property_account_receivable(self):
        self.ensure_one()
        account_receivable = self.property_account_receivable

        domain = [
            "|",
            ("code", "=", account_receivable),
            ("name", "=", account_receivable),
        ]
        property_account_receivable_id = self.env["account.account"].search(
            domain, limit=1
        )
        if property_account_receivable_id:
            return property_account_receivable_id

        domain = [
            ("property_account_receivable", "=", account_receivable),
            ("property_account_receivable_id", "!=", False),
        ]
        import_data = self.search(domain, limit=1)
        return (
            import_data.property_account_receivable_id
            if import_data.property_account_receivable_id
            else False
        )

    def _search_bank(self):
        self.ensure_one()

        domain = [("name", "=", self.bank_name)]
        bank_id = self.env["res.bank"].search(domain, limit=1)
        if bank_id:
            return bank_id

        domain = [
            ("bank_name", "=", self.bank_name),
            ("bank_id", "!=", False),
        ]
        import_data = self.search(domain, limit=1)
        return import_data.bank_id if import_data.bank_id else False

    def _search_property_account_position(self):
        self.ensure_one()

        domain = [("name", "=", self.property_account_position)]
        property_account_position_id = self.env["account.fiscal.position"].search(
            domain, limit=1
        )
        if property_account_position_id:
            return property_account_position_id

        domain = [
            ("property_account_position", "=", self.property_account_position),
            ("property_account_position_id", "!=", False),
        ]
        import_data = self.search(domain, limit=1)
        return (
            import_data.property_account_position_id
            if import_data.property_account_position_id
            else False
        )

    def _search_lang(self):
        self.ensure_one()

        import_data = self.search(
            [
                ("lang_char", "=", self.lang_char),
                ("lang", "!=", False),
            ],
            limit=1,
        )
        return import_data.lang if import_data.lang else ""

    # search datas linked by another tables
    def _compute_data(self):  # noqa: C901
        self.ensure_one()
        data = self._default_data()

        if not data["country_id"] and self.country and self._search_country():
            data["country_id"] = self._search_country()
            if not data["country_id"]:
                self.error = _("Country Not Found")
                return False
        if self.state and not data["state_id"] and not self._skip_compute_state():
            data["state_id"] = self._search_state(data["country_id"].id)
            if not data["state_id"]:
                self.error = _("State Not Found")
                return False
        if not data["property_payment_term_id"] and self.property_payment_term:
            data["property_payment_term_id"] = self._search_property_payment_term()
            if not data["property_payment_term_id"]:
                self.error = _("Customer Payment Terms Not Found")
                return False
        if (
            not data["property_supplier_payment_term_id"]
            and self.property_supplier_payment_term
        ):
            data["property_supplier_payment_term_id"] = (
                self._search_property_supplier_payment_term()
            )
            if not data["property_supplier_payment_term_id"]:
                self.error = _("Vendor Payment Terms Not Found")
                return False
        if not data["property_account_position_id"] and self.property_account_position:
            data["property_account_position_id"] = (
                self._search_property_account_position()
            )
            if not data["property_account_position_id"]:
                self.error = _("Fiscal Position Not Found")
                return False
        if not data["bank_id"] and self.bank_name:
            data["bank_id"] = self._search_bank()
            if not data["bank_id"]:
                self.error = _("Bank Not Found")
                return False
        if not data["property_account_payable_id"] and self.property_account_payable:
            data["property_account_payable_id"] = (
                self._search_property_account_payable()
            )
            if not data["property_account_payable_id"]:
                self.error = _("Account Payable Not Found")
                return False
        if (
            not data["property_account_receivable_id"]
            and self.property_account_receivable
        ):
            data["property_account_receivable_id"] = (
                self._search_property_account_receivable()
            )
            if not data["property_account_receivable_id"]:
                self.error = _("Account Receivable Not Found")
                return False
        if not data["lang"] and self.lang_char:
            data["lang"] = self._search_lang()
            if not data["lang"]:
                self.error = _("Lang Not Found (if not in list, lang not installed)")
                return False
        return data

    def _default_partner_data(self, partner_id):
        self.ensure_one()

        partner_data = {
            "company_type": "company" if self.is_company else "person",
            "vat": self.vat if self.vat else "",
            "street": self.street if self.street else "",
            "street2": self.street2 if self.street2 else "",
            "city": self.city if self.city else "",
            "zip": self.zip if self.zip else "",
            "phone": self.phone if self.phone else "",
            "mobile": self.mobile if self.mobile else "",
            "website": self.website if self.website else "",
            "email": self.email if self.email else "",
            "comment": self.comment if self.comment else "",
        }
        if not partner_id and self.ref:
            partner_data["ref"] = self.ref

        return partner_data

    def _prepare_partner_data(self, data, partner_id):
        self.ensure_one()
        partner_data = self._default_partner_data(partner_id)

        if data["state_id"]:
            partner_data["state_id"] = data["state_id"].id
        if data["country_id"]:
            partner_data["country_id"] = data["country_id"].id
        if data["property_payment_term_id"]:
            partner_data["property_payment_term_id"] = data[
                "property_payment_term_id"
            ].id
        if data["property_supplier_payment_term_id"]:
            partner_data["property_supplier_payment_term_id"] = data[
                "property_supplier_payment_term_id"
            ].id
        if data["property_account_position_id"]:
            partner_data["property_account_position_id"] = data[
                "property_account_position_id"
            ].id
        if data["property_account_payable_id"]:
            partner_data["property_account_payable_id"] = data[
                "property_account_payable_id"
            ].id
        if data["property_account_receivable_id"]:
            partner_data["property_account_receivable_id"] = data[
                "property_account_receivable_id"
            ].id
        if data["lang"]:
            partner_data["lang"] = data["lang"]

        return partner_data

    def set_other_partner_info(self, partner_id, data):
        self.ensure_one()

        partner_fields = self.env["res.partner"].fields_get()

        # optional data and based on installed modules
        if self.fiscalcode and "l10n_it_codice_fiscale" in partner_fields:
            if (
                not self.is_company
                and isinstance(self.fiscalcode, str)
                and len(self.fiscalcode) != 16
            ):
                self.error = _("Fiscal Code Not Valid")
                return False
            partner_id.l10n_it_codice_fiscale = self.fiscalcode

        if self.codice_destinatario and "l10n_it_pa_index" in partner_fields:
            partner_id.l10n_it_pa_index = self.codice_destinatario

        if self.pec_mail and "l10n_it_pec_email" in partner_fields:
            partner_id.l10n_it_pec_email = self.pec_mail

        if self.electronic_invoice_subjected:
            partner_id.display_invoice_edi_format = True
            partner_id.invoice_edi_format = "ubl_bis3"
            if "peppol_eas" in partner_fields:
                if partner_id.vat:
                    partner_id.peppol_eas = "0211"
                    partner_id.peppol_endpoint = partner_id.vat
                elif (
                    "l10n_it_codice_fiscale" in partner_fields
                    and partner_id.l10n_it_codice_fiscale
                ):
                    partner_id.peppol_eas = "0210"
                    partner_id.peppol_endpoint = partner_id.l10n_it_codice_fiscale

        if self.fax and "fax" in partner_fields:
            partner_id.fax = self.fax

        bank_id = data.get("bank_id")
        if bank_id and self.acc_number and partner_id:
            bank_vals = {
                "acc_number": self.acc_number,
                "partner_id": partner_id.id,
                "bank_id": bank_id.id,
            }
            self.env["res.partner.bank"].create([bank_vals])
        return True

    def auto_import_partner(self):
        imports_datas = self.search([("done", "=", False)])

        for import_data in imports_datas:
            if not import_data._check_consistency():
                continue

            # search partner
            partner_id = import_data._search_partner()

            # check partner
            if len(partner_id) != 1 and partner_id:
                import_data.error = _("There are many partner with same data")
                continue

            # prepare partner data
            data = import_data._compute_data()
            if not data:
                continue

            partner_data = import_data._prepare_partner_data(data, partner_id)

            # create/write partner
            if not partner_id:
                partner_data["name"] = import_data.partner_name
                try:
                    partner_id = self.env["res.partner"].create([partner_data])
                except Exception as error:
                    import_data.error = str(error)
                    continue
            else:
                try:
                    partner_id.write(partner_data)
                except Exception as error:
                    import_data.error = str(error)
                    continue

            # set partner info after update
            if not import_data.set_other_partner_info(partner_id, data):
                continue

            import_data.done = True
            self.env.cr.commit()  # pylint: disable=E8102
