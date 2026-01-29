#    Copyright (C) 2026 Xpmi srls (<xpmi@xpmi.it>)
# @author: Marco Calcagni (mcalcagni@xpmi.it)
# Dinamiche Aziendali srl (<http://www.dinamicheaziendali.it/>)
# @author: Giuseppe Borruso (gborruso@dinamicheaziendali.it)
# License GPL-3.0 or later (http://www.gnu.org/licenses/gpl.html).

from odoo import Command, _, fields, models


class XpmiToolsProductImport(models.Model):
    _name = "xpmi_tools.product_import"
    _description = "Product Import"

    name = fields.Char()
    list_price = fields.Float(string="Sales Price")
    detailed_type = fields.Selection(
        [
            ("consu", "Consumable"),
            ("service", "Service"),
            ("product", "Storable Product"),
            ("combo", "Combo"),
        ],
        string="Product Type",
        default="product",
        required=True,
    )
    product_default_code = fields.Char(required=True)
    barcode = fields.Char()
    categ = fields.Char(string="Product Category")
    categ_id = fields.Many2one("product.category", string="Product Category ID")
    description = fields.Html()
    supplier_ref = fields.Char(string="Supplier Reference")
    partner_id = fields.Many2one("res.partner", string="Partner")
    supplier_product_name = fields.Char()
    supplier_product_code = fields.Char()
    supplier_price = fields.Float()
    supplier_delay = fields.Integer(string="Supplier Delivery Lead Time")
    weight = fields.Float()
    volume = fields.Float()
    property_account_income = fields.Char(string="Income Account")
    property_account_income_id = fields.Many2one(
        "account.account", string="Income Account ID"
    )
    property_account_expense = fields.Char(string="Expense Account")
    property_account_expense_id = fields.Many2one(
        "account.account", string="Expense Account ID"
    )
    taxes = fields.Char(string="Customer Taxes")
    taxes_id = fields.Many2one(
        "account.tax",
        string="Customer Taxes ID",
        domain=[("type_tax_use", "=", "sale")],
    )
    supplier_taxes = fields.Char(string="Vendor Taxes")
    supplier_taxes_id = fields.Many2one(
        "account.tax",
        string="Vendor Taxes ID",
        domain=[("type_tax_use", "=", "purchase")],
    )
    tracking = fields.Selection(
        [
            ("serial", "By Unique Serial Number"),
            ("lot", "By Lots"),
            ("none", "No Tracking"),
        ],
        default="none",
        required=True,
    )
    uom = fields.Char(string="Unit of Measure")
    uom_id = fields.Many2one("uom.uom", string="Unit of Measure ID")
    uom_po = fields.Char(string="Purchase UoM")
    uom_po_id = fields.Many2one("uom.uom", string="Purchase UoM ID")
    active = fields.Boolean(default=True)
    done = fields.Boolean(default=False)
    error = fields.Char()

    def _check_consistency(self):
        self.ensure_one()
        self.error = ""

        if not self.product_default_code and not self.barcode:
            self.error = _("Set Product Default Code or Barcode")
            return False

        return True

    def _search_product(self):
        self.ensure_one()

        product_id = self.env["product.product"]
        if self.product_default_code:
            domain = [("default_code", "=", self.product_default_code)]
            product_id = self.env["product.product"].search(domain, limit=1)
        if not product_id and self.barcode:
            domain = [("barcode", "=", self.barcode)]
            product_id = self.env["product.product"].search(domain, limit=1)
        return product_id

    def _default_data(self):
        self.ensure_one()

        data = {
            "property_account_income_id": (
                self.property_account_income_id or self.env["account.account"]
            ),
            "property_account_expense_id": (
                self.property_account_expense_id or self.env["account.account"]
            ),
            "taxes_id": self.taxes_id or self.env["account.tax"],
            "supplier_taxes_id": self.supplier_taxes_id or self.env["account.tax"],
            "categ_id": self.categ_id or self.env["product.category"],
            "uom_id": self.uom_id or self.env["uom.uom"],
            "uom_po_id": (
                self.uom_po_id if self.uom_po_id else self.uom_id or self.env["uom.uom"]
            ),
        }
        return data

    def _search_property_account_income(self):
        self.ensure_one()

        domain = [
            ("code", "=", self.property_account_income),
        ]
        property_account_income_id = self.env["account.account"].search(domain, limit=1)
        if property_account_income_id:
            return property_account_income_id

        domain = [
            ("property_account_income", "=", self.property_account_income),
            ("property_account_income_id", "!=", False),
        ]
        import_data = self.search(domain, limit=1)
        return (
            import_data.property_account_income_id
            if import_data.property_account_income_id
            else False
        )

    def _search_property_account_expense(self):
        self.ensure_one()

        domain = [
            ("code", "=", self.property_account_expense),
        ]
        property_account_expense_id = self.env["account.account"].search(
            domain, limit=1
        )
        if property_account_expense_id:
            return property_account_expense_id

        domain = [
            ("property_account_expense", "=", self.property_account_expense),
            ("property_account_expense_id", "!=", False),
        ]
        import_data = self.search(domain, limit=1)
        return (
            import_data.property_account_expense_id
            if import_data.property_account_expense_id
            else False
        )

    def _search_taxes(self):
        self.ensure_one()

        domain = [
            ("taxes", "=", self.taxes),
            ("taxes_id", "!=", False),
        ]
        import_data = self.search(domain, limit=1)
        return import_data.taxes_id if import_data.taxes_id else False

    def _search_supplier_taxes(self):
        self.ensure_one()

        domains = [
            [
                ("supplier_taxes", "=", self.supplier_taxes),
                ("supplier_taxes_id", "!=", False),
            ],
            [("taxes", "=", self.supplier_taxes), ("supplier_taxes_id", "!=", False)],
        ]
        for domain in domains:
            import_data = self.search(domain, limit=1)
            if import_data and import_data.supplier_taxes_id:
                return import_data.supplier_taxes_id

        return False

    def _search_categ(self):
        self.ensure_one()

        domain = [("name", "=ilike", self.categ)]
        categ_id = self.env["product.category"].search(domain, limit=1)
        if categ_id:
            return categ_id

        domain = [
            ("categ", "=ilike", self.categ),
            ("categ_id", "!=", False),
        ]
        import_data = self.search(domain, limit=1)
        return import_data.categ_id if import_data.categ_id else False

    def _search_uom(self):
        self.ensure_one()

        domain = [("name", "=ilike", self.uom)]
        uom_id = self.env["uom.uom"].search(domain, limit=1)
        if uom_id:
            return uom_id

        domain = [
            ("uom", "=ilike", self.uom),
            ("uom_id", "!=", False),
        ]
        import_data = self.search(domain, limit=1)
        return import_data.uom_id if import_data.uom_id else False

    def _search_uom_po(self):
        self.ensure_one()

        domain = [("name", "=ilike", self.uom_po)]
        uom_po_id = self.env["uom.uom"].search(domain, limit=1)
        if uom_po_id:
            return uom_po_id

        domains = [
            [("uom_po", "=", self.uom_po), ("uom_po_id", "!=", False)],
            [("uom", "=", self.uom_po), ("uom_po_id", "!=", False)],
        ]
        for domain in domains:
            import_data = self.search(domain, limit=1)
            if import_data and import_data.uom_po_id:
                return import_data.uom_po_id

        return False

    def _compute_data(self):
        # flake8: noqa: C901
        self.ensure_one()
        data = self._default_data()

        if not data["property_account_income_id"]:
            data["property_account_income_id"] = self._search_property_account_income()
        if not data["property_account_income_id"]:
            self.error = _("Income Account Not Found")
            return False

        if not data["property_account_expense_id"]:
            data["property_account_expense_id"] = (
                self._search_property_account_expense()
            )
        if not data["property_account_expense_id"]:
            self.error = _("Expense Account Not Found")
            return False

        if not data["taxes_id"] and self.taxes:
            data["taxes_id"] = self._search_taxes()
        if not data["taxes_id"]:
            self.error = _("Customer Taxes Not Found")
            return False

        if not self.supplier_taxes:
            self.supplier_taxes = self.taxes
        if not data["supplier_taxes_id"] and self.supplier_taxes:
            data["supplier_taxes_id"] = self._search_supplier_taxes()
        if not data["supplier_taxes_id"]:
            self.error = _("Vendor Taxes Not Found")
            return False

        if not data["categ_id"] and self.categ:
            data["categ_id"] = self._search_categ()
        if not data["categ_id"]:
            self.error = _("Product Category Not Found")
            return False

        if not data["uom_id"] and self.uom:
            data["uom_id"] = self._search_uom()
        if not data["uom_id"]:
            self.error = _("Unit of Measure Not Found")
            return False

        if not self.uom_po:
            self.uom_po = self.uom
        if not data["uom_po_id"] and self.uom_po:
            data["uom_po_id"] = self._search_uom_po()
        if not data["uom_po_id"]:
            self.error = _("Purchase UoM Not Found")
            return False

        return data

    def _default_product_data(self, product_id):
        self.ensure_one()

        product_data = {
            "list_price": self.list_price or "",
            "weight": product_id.weight or self.weight,
            "volume": product_id.volume or self.volume,
            "barcode": product_id.barcode or self.barcode,
            "description": product_id.description or self.description,
            "default_code": product_id.default_code or self.product_default_code,
        }
        if not product_id.type:
            if self.detailed_type == "product":
                product_data["is_storable"] = True
                product_data["type"] = "consu"
                product_data["tracking"] = product_id.tracking or self.tracking
            else:
                product_data["type"] = self.detailed_type
        else:
            product_data["type"] = product_id.type
        return product_data

    def _prepare_product_data(self, data, product_id):
        self.ensure_one()
        product_data = self._default_product_data(product_id)

        if (
            data["property_account_income_id"]
            and not product_id.property_account_income_id
        ):
            product_data["property_account_income_id"] = data[
                "property_account_income_id"
            ].id
        if (
            data["property_account_income_id"]
            and not product_id.property_account_income_id
        ):
            product_data["property_account_income_id"] = data[
                "property_account_income_id"
            ].id
        if (
            data["property_account_expense_id"]
            and not product_id.property_account_expense_id
        ):
            product_data["property_account_expense_id"] = data[
                "property_account_expense_id"
            ].id
        if data["taxes_id"] and not product_id.taxes_id:
            product_data["taxes_id"] = [Command.set([data["taxes_id"].id])]
        if data["supplier_taxes_id"] and not product_id.supplier_taxes_id:
            product_data["supplier_taxes_id"] = [
                Command.set([data["supplier_taxes_id"].id])
            ]
        if data["categ_id"] and not product_id.categ_id:
            product_data["categ_id"] = data["categ_id"].id
        if data["uom_id"] and not product_id.uom_id:
            product_data["uom_id"] = data["uom_id"].id
        if not product_id.uom_po_id:
            if data["uom_po_id"]:
                product_data["uom_po_id"] = data["uom_po_id"].id
            elif data["uom_id"]:
                product_data["uom_po_id"] = data["uom_id"].id

        return product_data

    def _search_supplier(self):
        self.ensure_one()

        domain = [("ref", "=", self.supplier_ref)]
        partner_id = self.env["res.partner"].search(domain, limit=1)
        if partner_id:
            return partner_id

        domain = [("ref", "ilike", self.supplier_ref)]
        partner_id = self.env["res.partner"].search(domain, limit=1)
        if partner_id:
            partner_ref = partner_id.ref or ""
            if self.supplier_ref in partner_ref.split():
                return partner_id

        domain = [
            ("supplier_ref", "=", self.supplier_ref),
            ("partner_id", "!=", False),
        ]
        import_data = self.search(domain, limit=1)
        return import_data.partner_id if import_data.partner_id else False

    def manage_supplier_data(self, product_id):
        self.ensure_one()

        # search supplier
        if not self.partner_id:
            partner_id = self._search_supplier()
            if not partner_id:
                self.error = _("Supplier Not Found")
                return False
            else:
                partner_id = partner_id.id
        else:
            partner_id = self.partner_id.id

        # search supplier product
        domain = [
            ("partner_id", "=", partner_id),
            ("product_id", "=", product_id.id),
        ]
        supplier_info = self.env["product.supplierinfo"].search(domain, limit=1)

        # set info supplier
        if not supplier_info:
            supplier_info_data = {
                "partner_id": partner_id,
                "product_tmpl_id": product_id.product_tmpl_id.id,
                "product_id": product_id.id,
                "product_name": self.supplier_product_name,
                "product_code": self.supplier_product_code,
                "delay": self.supplier_delay,
                "price": self.supplier_price,
            }
            self.env["product.supplierinfo"].create([supplier_info_data])
        else:
            supplier_info.product_name = (
                self.supplier_product_name or supplier_info.product_name
            )
            supplier_info.product_code = (
                self.supplier_product_code or supplier_info.product_code
            )
            supplier_info.delay = self.supplier_delay or supplier_info.delay
            supplier_info.price = self.supplier_price or supplier_info.price

    def auto_import_product(self):
        imports_datas = self.search([("done", "=", False)])

        for import_data in imports_datas:
            if not import_data._check_consistency():
                continue

            # search product
            product_id = import_data._search_product()
            if len(product_id) != 1 and product_id:
                import_data.error = _("There are many partner with same data")
                continue

            # prepare product data
            data = import_data._compute_data()
            if not data:
                continue

            product_data = import_data._prepare_product_data(data, product_id)

            # create/write product
            if not product_id:
                product_data["name"] = import_data.name
                try:
                    product_id = self.env["product.product"].create([product_data])
                except Exception as error:
                    import_data.error = str(error)
                    continue
            else:
                try:
                    product_id.write(product_data)
                except Exception as error:
                    import_data.error = str(error)
                    continue

            # if I have supplier write supplier data
            if import_data.partner_id or import_data.supplier_ref:
                import_data.manage_supplier_data(product_id)

            import_data.done = True
            self.env.cr.commit()  # pylint: disable=E8102
