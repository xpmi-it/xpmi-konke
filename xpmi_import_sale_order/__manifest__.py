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
##############################################################################

{
    "name": "Xpmi - Utility per importare importare ordini clienti",
    "summary": "Utility per importare importare ordini clienti",
    "author": "Xpmi srls",
    "license": "AGPL-3",
    "website": "https://www.xpmi.it/",
    "category": "Xpmi Tools/Import",
    "version": "18.0.1.0.0",
    "depends": [
        "sale",
        "xpmi_import",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/xpmi_tools_sale_order.xml",
    ],
    "images": ["static/description/icon.png"],
    "installable": True,
}
