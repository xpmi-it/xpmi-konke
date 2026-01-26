# -*- coding: utf-8 -*-
# Copyright (C) 2023-Today:
#     Dinamiche Aziendali srl (<http://www.dinamicheaziendali.it/>)
# @author: Gianmarco Conte (gconte@dinamicheaziendali.it)
# License GPL-3.0 or later (http://www.gnu.org/licenses/gpl.html).

{
    'name': "Da Connetor Mirakl",
    'summary': "",
    'license': 'Other proprietary',
    'description': "Connector Mirakl",
    'author': 'Gianmarco Conte <gconte@dinamicheaziendali.it> ',
    'website': 'www.dinamicheaziendali.it',
    'category': 'Sales',
    'version': '18.0.1.0',
    'depends': [
        'base',
        'stock',
        'delivery',
        'sale',
        'da_connector_base',
        'da_connector_partner',
        'da_connector_sale_order',
        'da_connector_stock',
        'da_connector_mapping_product',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/automated_action.xml',
        'views/connector_setting_view.xml',
        'views/delivery_carrier_view.xml',
        'views/product_customerinfo_view.xml',
        'wizard/accept_order_mirakl_wizard_view.xml',
    ],
    'demo': [],
    'active': False,
    'installable': True
}
