from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    hide_email_layout_parts = fields.Boolean(
        string="Nascondi header e footer email",
        help=(
            "Se attivo, rimuove il titolo automatico, "
            "il footer aziendale e 'Powered by Odoo' "
            "dalle email di notifica."
        ),
        default=False,
    )
