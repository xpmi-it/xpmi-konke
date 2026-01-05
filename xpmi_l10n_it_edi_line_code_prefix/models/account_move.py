import logging
from odoo import models

_logger = logging.getLogger(__name__)

_logger.info("l10n_it_edi_line_code_prefix: module loaded (account_move.py imported)")


class AccountMove(models.Model):
    _inherit = "account.move"

    def _l10n_it_edi_import_line(self, element, move_line, extra_info):
        _logger.info(
            "l10n_it_edi_line_code_prefix: _l10n_it_edi_import_line CALLED move_id=%s line_id=%s",
            self.id if len(self) == 1 else self.ids,
            move_line.id if move_line else None,
        )

        # Let Odoo handle the standard logic (including possible product lookup)
        res = super()._l10n_it_edi_import_line(element, move_line, extra_info)

        # If Odoo found a product, do not change anything
        if move_line.product_id:
            _logger.debug("l10n_it_edi_line_code_prefix: product found (%s), skip", move_line.product_id.id)
            return res

        # Description (already set by Odoo)
        description = (move_line.name or "").strip()
        if not description or description.startswith("["):
            return res

        codice_valore = None

        # Priority: CodiceTipo=Fornitore, fallback to the first available one
        for codice_node in element.findall(".//CodiceArticolo"):
            tipo = (codice_node.findtext("CodiceTipo") or "").strip()
            valore = (codice_node.findtext("CodiceValore") or "").strip()
            _logger.debug(
                "l10n_it_edi_line_code_prefix: found CodiceArticolo tipo=%r valore=%r",
                tipo,
                valore,
            )
            if valore:
                if tipo == "Fornitore":
                    codice_valore = valore
                    break
                if not codice_valore:
                    codice_valore = valore

        if codice_valore:
            new_name = f"[{codice_valore}] {description}"
            move_line.name = new_name
            _logger.info("l10n_it_edi_line_code_prefix: line name updated -> %r", new_name)

        return res
