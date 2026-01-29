# -*- coding: utf-8 -*-
# Copyright (C) 2023-Today:
#     Dinamiche Aziendali srl (<http://www.dinamicheaziendali.it/>)
# @author: Gianmarco Conte (gconte@dinamicheaziendali.it)
# License GPL-3.0 or later (http://www.gnu.org/licenses/gpl.html).
from odoo import fields, models, api
import requests
import json
import csv
import io
import base64
import paramiko
from datetime import datetime, timedelta

header = ['gtin', 'stock']
header_pricelist = ['gtin', 'sku', 'selling_price',
                    'manufacturer_recommended_price', 'tax_rate_percentage']


class ConnectorSettingInherit(models.Model):
    _inherit = 'connector.setting'

    a = {
        "orders": [
            {
                "acceptance_decision_date": "2023-02-02T12:36:07Z",
                "commercial_id": "005-23033L5441",
                "customer": {
                    "billing_address": {
                        "city": "Montecatini Terme",
                        "company": "R-sub di Tacchi Riccardo",
                        "company_2": 'null',
                        "country": "IT",
                        "country_iso_code": "ITA",
                        "firstname": "Riccardo",
                        "lastname": "Tacchi",
                        "state": "Pistoia",
                        "street_1": "via manin 19",
                        "street_2": "r.sub",
                        "zip_code": "51016"
                    },
                    "civility": 'null',
                    "customer_id": "5-65225033",
                    "firstname": "Riccardo",
                    "lastname": "Tacchi",
                    "locale": "it_IT",
                    "shipping_address": {
                        "additional_info": 'null',
                        "city": "Montecatini Terme",
                        "company": "R-sub di Tacchi Riccardo",
                        "company_2": 'null',
                        "country": "IT",
                        "country_iso_code": "ITA",
                        "firstname": "Riccardo",
                        "lastname": "Tacchi",
                        "phone": "+393334446411",
                        "state": "Pistoia",
                        "street_1": "via manin 19",
                        "street_2": "r.sub",
                        "zip_code": "51016"
                    }
                },
                "customer_debited_date": "2023-02-02T12:40:35.272Z",
                "customer_notification_email": "rfx1qmo581n.ko8qhtg3z@notification.mirakl.net",
                "delivery_date": {
                    "earliest": "2023-02-04T09:56:46.814Z",
                    "latest": "2023-02-07T09:56:46.814Z"
                },
                "fulfillment": {
                    "center": {
                        "code": "DEFAULT"
                    }
                },
                "fully_refunded": 'false',
                "has_customer_message": 'false',
                "order_additional_fields": [
                    {
                        "code": "administrative-tax-code",
                        "type": "STRING",
                        "value": "riccardotacchi@legalmail.it;00474170479;W4KYJ8V"
                    },
                    {
                        "code": "client-type",
                        "type": "LIST",
                        "value": "INH"
                    },
                    {
                        "code": "invoice-organization-type",
                        "type": "STRING",
                        "value": "ALTRO"
                    }
                ],
                "order_lines": [
                    {
                        "can_refund": 'true',
                        "category_code": "201981|ESCABEAU|ESCABEAU_MARCHEPIED|R10-011-005",
                        "category_label": "Scala",
                        "commission_fee": 15.60,
                        "commission_rate_vat": 0.0000,
                        "commission_taxes": [
                            {
                                "amount": 0.00,
                                "code": "TAXZERO",
                                "rate": 0.0000
                            }
                        ],
                        "commission_vat": 0.00,
                        "debited_date": "2023-02-02T12:40:35Z",
                        "description": 'null',
                        "last_updated_date": "2023-02-23T15:26:51Z",
                        "offer_id": 1081795,
                        # "offer_sku": "LDR-JC4X4-MLT",
                        "offer_state_code": "11",
                        "order_line_additional_fields": [
                            {
                                "code": "precalculated-shipment-origin",
                                "type": "LIST",
                                "value": "IT"
                            },
                            {
                                "code": "product-title",
                                "type": "STRING",
                                "value": "Boudech - Rig-4x4 Scala Pieghevole Multiuso In Alluminio Con Piattaforma A Ponteggio Per Impalcatura"
                            },
                            {
                                "code": "seller-updated-shipment-origin",
                                "type": "LIST",
                                "value": "IT"
                            }
                        ],
                        "order_line_id": "8aaf6bd6-5846-4bf0-9bed-b1537d6dfa39",
                        "order_line_state": "RECEIVED",
                        # "price": 129.99,
                        "price_amount_breakdown": {
                            "parts": [
                                {
                                    "amount": 106.55,
                                    "commissionable": 'true',
                                    "debitable_from_customer": 'true',
                                    "payable_to_shop": 'true'
                                },
                                {
                                    "amount": 23.44,
                                    "commissionable": 'true',
                                    "debitable_from_customer": 'true',
                                    "payable_to_shop": 'true'
                                }
                            ]
                        },
                        # "price_unit": 129.99,
                        "product_title": "Boudech - Rig-4x4 Plate-forme D'échafaudage Pliable Et Polyvalente En Aluminium Échafaudage",
                        "promotions": [],
                        "received_date": "2023-02-23T15:26:51Z",
                        "refunds": [],
                        "shipped_date": "2023-02-02T13:33:37Z",
                        "shipping_price": 0.00,
                        "shipping_price_additional_unit": 'null',
                        "shipping_price_amount_breakdown": {
                            "parts": [
                                {
                                    "amount": 0.00,
                                    "commissionable": 'true',
                                    "debitable_from_customer": 'true',
                                    "payable_to_shop": 'true'
                                },
                                {
                                    "amount": 0.00,
                                    "commissionable": 'true',
                                    "debitable_from_customer": 'true',
                                    "payable_to_shop": 'true'
                                }
                            ]
                        },
                        "shipping_price_unit": 'null',
                        "shipping_taxes": [
                            {
                                "amount": 0.00,
                                "amount_breakdown": {
                                    "parts": [
                                        {
                                            "amount": 0.00,
                                            "commissionable": 'true',
                                            "debitable_from_customer": 'true',
                                            "payable_to_shop": 'true'
                                        }
                                    ]
                                },
                                "code": "ITVATSTD",
                                "rate": 22.0000,
                                "tax_calculation_rule": "PROPORTIONAL_TO_AMOUNT"
                            }
                        ],
                        "taxes": [
                            {
                                "amount": 23.44,
                                "amount_breakdown": {
                                    "parts": [
                                        {
                                            "amount": 23.44,
                                            "commissionable": 'true',
                                            "debitable_from_customer": 'true',
                                            "payable_to_shop": 'true'
                                        }
                                    ]
                                },
                                "code": "ITVATSTD",
                                "rate": 22.0000,
                                "tax_calculation_rule": "PROPORTIONAL_TO_AMOUNT"
                            }
                        ],
                        "total_commission": 15.60,
                        "total_price": 129.99
                    }
                ],
                "order_state_reason_code": "AUTO_RECEIVED",
                "order_state_reason_label": "Ricevuto automaticamente",
                "order_tax_mode": "TAX_INCLUDED",
                "payment_workflow": "PAY_ON_ACCEPTANCE",
                # "price": 129.99,
                "promotions": {
                    "applied_promotions": [],
                    "total_deduced_amount": 0
                },
            }]}
