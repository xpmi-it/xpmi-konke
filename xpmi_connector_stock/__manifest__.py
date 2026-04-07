# -*- coding: utf-8 -*-
# Copyright (C) 2023-Today:
#     Dinamiche Aziendali srl (<http://www.dinamicheaziendali.it/>)
# @author: Gianmarco Conte (gconte@dinamicheaziendali.it)
# License GPL-3.0 or later (http://www.gnu.org/licenses/gpl.html).

{
    'name': "Connector Stock",
    'summary': "",
    'license': 'Other proprietary',
    # 'price': '249.99',
    # 'currency': 'EUR',
    'description': "Connector Stock",
    'author': 'Gianmarco Conte <gconte@dinamicheaziendali.it> ',
    'website': 'www.dinamicheaziendali.it',
    'category': 'Sales',
    'version': '18.0.1.0',
    'depends': [
        'base',
        'stock',
        'sale',
        'sales_team',
        'da_connector_base',
    ],
    'data': [
        'data/ir_config_parameter.xml',
        'data/automated_action.xml',
        'security/ir.model.access.csv',
        'views/connector_stock_view.xml',
        'views/connector_setting_view.xml',
        'views/product_view.xml',
    ],
    'demo': [],
    'active': False,
    'installable': True
}
