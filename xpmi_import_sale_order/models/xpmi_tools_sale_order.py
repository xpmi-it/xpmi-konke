##############################################################################
#
#    Copyright (C) 2026 Xpmi srls (<xpmi@xpmi.it>)
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################


from odoo import api, fields, models


class DaToolsSaleOrder(models.Model):
    _name = "xpmi_tools.sale_order_import"
    _description = "Import Sale Orders"
    _rec_name = "number"

    active = fields.Boolean(string="Attiva", default=True)
    evaso = fields.Boolean(default=False)
    errore = fields.Char()
    number = fields.Char(string="Numero ordine")
    client_order_ref = fields.Char(string="Riferimento ordine cliente")
    client_code = fields.Char(string="Codice cliente")
    invoice_code = fields.Char(string="Codice a cui fatturare")
    delivery_code = fields.Char(string="Codice a cui spedire")
    date = fields.Date(string="Data ordine")
    date_delivery = fields.Date(string="Data prevista consegna")
    product_code = fields.Char(string="Codice articolo")
    descrizione = fields.Char()
    qty = fields.Float(string="Quantità")
    prezzo_unitario = fields.Float(string="Prezzo unitario")
    sconto = fields.Float(string="Sconto 1 %")
    sconto2 = fields.Float(string="Sconto 2 %")
    sconto3 = fields.Float(string="Sconto 3 %")

    def _search_partner(self, ref_code):
        if not ref_code:
            return None

        domain = ["|", ("ref", "=", ref_code), ("ref", "ilike", ref_code)]
        return self.env["res.partner"].search(domain, limit=1)

    @api.model
    def hook_update_sale_order(self, sale_order):
        """Hook for many update after creation from other modules"""
        if not sale_order:
            return False

        # sale_order.onchange_partner_id()
        # sale_order.onchange_partner_id_warning()
        # sale_order.onchange_partner_shipping_id()
        if self.date_delivery:
            sale_order._onchange_commitment_date()
        if hasattr(self.env["sale.order"], "type_id"):
            sale_order.onchange_type_id()
        return True

    def get_key_number(self):
        return " ".join(filter(None, [self.client_code, self.client_order_ref]))

    def auto_set_number(self):
        import_datas = self.search([("evaso", "=", False), ("number", "=", False)])
        number_dict = {}
        for import_data in import_datas:
            key_number = import_data.get_key_number()
            if key_number in number_dict:
                continue

            seq_date = import_data.date and fields.Datetime.context_timestamp(
                self, fields.Datetime.to_datetime(import_data.date)
            )

            if hasattr(self.env["sale.order"], "type_id"):
                partner = self._search_partner(import_data.client_code)
                if not partner:
                    import_data.errore = "Cliente non trovato"
                    continue

                sale_type = (
                    partner.with_company(self.env.company).sale_type
                    if partner
                    else False
                )
                if not sale_type:
                    sale_type = (
                        self.env["sale.order"]
                        .default_get(["type_id"])
                        .get("type_id", False)
                    )
                if not sale_type:
                    sale_type = self.env["sale.order"]._default_type_id()

                number_dict[key_number] = sale_type.sequence_id.next_by_id(
                    sequence_date=seq_date
                ) or self.env["ir.sequence"].next_by_code(
                    "sale.order", sequence_date=seq_date
                )
            else:
                number_dict[key_number] = self.env["ir.sequence"].next_by_code(
                    "sale.order", sequence_date=seq_date
                )
        for import_data in import_datas:
            key_number = import_data.get_key_number()
            import_data.number = number_dict[key_number]

    def _prepare_order_vals(self, partner, ship_partner, inv_partner):
        vals = {
            "name": self.number,
            "client_order_ref": self.client_order_ref,
            "partner_id": partner.id,
            "partner_shipping_id": ship_partner.id,
            "partner_invoice_id": inv_partner.id,
            "company_id": self.env.company.id,
            "state": "draft",
        }
        if self.date:
            vals["date_order"] = self.date
        if self.date_delivery:
            vals["commitment_date"] = self.date_delivery
        if hasattr(self.env["sale.order"], "type_id"):
            sale_type = partner.with_company(self.env.company).sale_type
            if not sale_type:
                sale_type = (
                    self.env["sale.order"]
                    .default_get(["type_id"])
                    .get("type_id", False)
                )
            if not sale_type:
                sale_type = self.env["sale.order"]._default_type_id()
            vals["type_id"] = sale_type.id
        return vals

    def _prepare_line_vals(self, product, route_id=None):
        line_vals = {
            "product_id": product.id,
            "product_uom_qty": self.qty,
            "discount": self.sconto,
        }
        if self.prezzo_unitario:
            line_vals["price_unit"] = self.prezzo_unitario
        if self.descrizione:
            line_vals["name"] = self.descrizione
        if route_id:
            line_vals["route_id"] = route_id.id
        if "discount2" in self.env["sale.order.line"].fields_get():
            line_vals["discount2"] = self.sconto2
        if "discount3" in self.env["sale.order.line"].fields_get():
            line_vals["discount3"] = self.sconto3
        return line_vals

    def auto_import_sale_order(self):
        imports_datas = self.search([("evaso", "=", False)])
        if not imports_datas:
            return True

        prod_codes = imports_datas.mapped("product_code")
        prods = self.env["product.product"].search([("default_code", "in", prod_codes)])
        prod_map = {p.default_code: p for p in prods}

        self.auto_set_number()

        for import_data in imports_datas:
            # svuoto errore
            import_data.errore = ""

            if not import_data.client_code:
                import_data.errore = "Errore manca codice cliente"
                continue
            if not import_data.product_code:
                import_data.errore = "Errore articolo"
                continue

            # controllo cliente
            partner = import_data._search_partner(import_data.client_code)
            if not partner:
                import_data.errore = "Cliente non trovato"
                continue

            # controllo prodotto
            product = prod_map.get(import_data.product_code)
            if not product:
                import_data.errore = "Manca product con riferimento interno"
                continue

            # controllo indirizzo consegna
            ship_partner = (
                import_data._search_partner(import_data.delivery_code) or partner
            )
            if not ship_partner:
                import_data.errore = "Indirizzo di consegna non trovato"
                continue

            # controllo indirizzo fattura
            inv_partner = (
                import_data._search_partner(import_data.invoice_code) or partner
            )
            if not inv_partner:
                import_data.errore = "Indirizzo di fatturazione non trovato"
                continue

            # controllo ordine
            domain = [("name", "=", import_data.number), ("state", "=", "draft")]
            order = self.env["sale.order"].search(domain, limit=1)
            if not order:
                vals = import_data._prepare_order_vals(
                    partner, ship_partner, inv_partner
                )
                order = self.env["sale.order"].create(vals)
                import_data.hook_update_sale_order(order)

            # aggiungo le righe
            if hasattr(self.env["sale.order"], "type_id"):
                route = (
                    order.type_id.route_id if hasattr(order.type_id, "route_id") else None
                )
            else:
                route = False


            line_vals = import_data._prepare_line_vals(product, route)
            self.env["sale.order.line"].create({**line_vals, "order_id": order.id})

            import_data.evaso = True

        return True
