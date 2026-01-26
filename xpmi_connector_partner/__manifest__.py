# -*- coding: utf-8 -*-
# Copyright (C) 2023-Today:
#     Dinamiche Aziendali srl (<http://www.dinamicheaziendali.it/>)
# @author: Gianmarco Conte (gconte@dinamicheaziendali.it)
# License GPL-3.0 or later (http://www.gnu.org/licenses/gpl.html).

{
    'name': "Base External Connector",
    'summary': "",
    'license': 'Other proprietary',
    # 'price': '249.99',
    # 'currency': 'EUR',
    'description': "Base module for external Connector",
    'author': 'Gianmarco Conte <gconte@dinamicheaziendali.it> ',
    'website': 'www.dinamicheaziendali.it',
    'category': 'Sales',
    'version': '18.0.1.0',
    'depends': [
        'base',
        'stock',
        'sale',
        'da_connector_base',
        'l10n_it_edi',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/connector_setting_view.xml',
        'views/connector_partner_view.xml',
    ],
    "external_dependencies": {
        "python": ["codicefiscale"],
    },
    'demo': [],
    'active': False,
    'installable': True
}
