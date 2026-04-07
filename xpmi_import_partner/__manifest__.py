# Copyright (C) 2023-Today:
# Xpmi srls (<http://www.xpmi.it/>)
# @author: Marco Calcagni (mcalcagni@xpmi.it)
# @author: Giuseppe Borruso (gborruso@dinamicheaziendali.it)
# License GPL-3.0 or later (http://www.gnu.org/licenses/gpl.html).

{
    "name": "Xpmi - Utility Per Importare Partner",
    "version": "18.0.1.0.0",
    "category": "Xpmi Tools/Import",
    "summary": "Permette di importare partner",
    "author": "Xpmi srls",
    "website": "https://www.xpmi.it/",
    "license": "AGPL-3",
    "depends": [
        "contacts",
        "account",
        "xpmi_import",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/xpmi_tools_partner.xml",
    ],
    "images": ["static/description/icon.png"],
    "installable": True,
}
