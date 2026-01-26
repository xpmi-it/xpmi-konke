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
        'sales_team',
    ],
    'data': [
        'security/res_groups.xml',
        'security/ir.model.access.csv',
        'views/menu.xml',
        'views/connector_mapping_view.xml',
        'views/connector_setting_view.xml',
    ],
    'demo': [],
    'active': False,
    'installable': True
}
