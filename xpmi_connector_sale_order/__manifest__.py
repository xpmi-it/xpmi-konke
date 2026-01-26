# -*- coding: utf-8 -*-
# Copyright (C) 2023-Today:
#     Dinamiche Aziendali srl (<http://www.dinamicheaziendali.it/>)
# @author: Gianmarco Conte (gconte@dinamicheaziendali.it)
# License GPL-3.0 or later (http://www.gnu.org/licenses/gpl.html).

{
    'name': "Order External Connector",
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
        'delivery',
        'sale',
        'sales_team',
        'da_connector_base',
        'da_connector_mapping_product',
        'sale_order_type',
    ],
    'data': [
        'data/automated_action.xml',
        'security/ir.model.access.csv',
        'views/connector_setting_view.xml',
        'views/connector_order_view.xml',
        'views/connector_carrier_view.xml',
        'views/sale_order_view.xml',
        'wizard/wizard_order_import.xml',
    ],
    'demo': [],
    'active': False,
    'installable': True
}
