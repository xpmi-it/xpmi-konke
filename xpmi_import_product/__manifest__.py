# Copyright (C) 2023-Today:
#    Copyright (C) 2026 Xpmi srls (<xpmi@xpmi.it>)
# @author: Marco Calcagni (mcalcagni@xpmi.it)
# @author: Giuseppe Borruso (gborruso@dinamicheaziendali.it)
# License GPL-3.0 or later (http://www.gnu.org/licenses/gpl.html).

{
    "name": "Xpmi - Utility Per Importare Prodotti",
    "version": "18.0.1.0.0",
    "category": "Xpmi Tools/Import",
    "summary": "Permette di importare prodotti",
    "author": "Xpmi srls",
    "website": "https://www.xpmi.it/",
    "license": "AGPL-3",
    "depends": [
        "sale",
        "purchase",
        "product",
        "xpmi_import",
        "stock",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/xpmi_tools_product.xml",
    ],
    "images": ["static/description/icon.png"],
    "installable": True,
}
