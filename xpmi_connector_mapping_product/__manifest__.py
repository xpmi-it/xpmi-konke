# -*- coding: utf-8 -*-
# Copyright (C) 2023-Today:
#     Dinamiche Aziendali srl (<http://www.dinamicheaziendali.it/>)
# @author: Gianmarco Conte (gconte@dinamicheaziendali.it)
# License GPL-3.0 or later (http://www.gnu.org/licenses/gpl.html).

{
    'name': "Connector - Mapping product",
    'summary': "",
    'license': 'Other proprietary',
    'description': "Connector - Mapping product",
    'author': 'Gianmarco Conte <gconte@dinamicheaziendali.it> ',
    'website': 'www.dinamicheaziendali.it',
    'category': 'Sales',
    'version': '18.0.1.0',
    'depends': [
        'base',
        'da_connector_base',
        'product_supplierinfo_for_customer',
    ],
    'data': [
        # 'security/ir.model.access.csv',
        'views/product_customerinfo_view.xml',
    ],
    'demo': [],
    'active': False,
    'installable': True
}
