# -*- coding: utf-8 -*-
# Copyright (C) 2023-Today:
#     Dinamiche Aziendali srl (<http://www.dinamicheaziendali.it/>)
# @author: Gianmarco Conte (gconte@dinamicheaziendali.it)
# License GPL-3.0 or later (http://www.gnu.org/licenses/gpl.html).
from odoo import fields, models, api


class ConnectorSettingInherit(models.Model):
    _inherit = 'connector.setting'

    import_order = fields.Boolean(string='Import Orders')
    order_status_to_import = fields.Char(string='Order status to import',
                                         help="A comma-separated list of order state's "
                                              "codes based on marketplace values,"
                                              "for example: STAGING, WAITING_ACCEPTANCE, WAITING_DEBIT")
    range_import_order = fields.Selection([("today", "Today"),
                                           ("since_yesterday", "Since Yesterday"),
                                           ("last_7_days", "Last 7 Days"),
                                           ],
                                          string='Range Import Orders')
    url_import_order = fields.Char(string='Url Import Orders')
    url_carrier_info = fields.Char(string='Url Carrier Info')
    limit_for_call = fields.Integer(string='Limit Nr. Order for every call',
                                    help='This is number of orders to import in single call API.'
                                         'It is used only for marketplace that allows to set this number')
    discount_product_id = fields.Many2one('product.product', string='Discount Product')
    order_prefix = fields.Char(string='Order Prefix')
    use_odoo_sequence = fields.Boolean(string='Use Odoo Sequence')
    carrier_id = fields.Many2one('delivery.carrier', string='Delivery Method',
                                 help='Default Delivery Method on Sale Order')
    automatic_confirm_sale_order = fields.Boolean(string='Automatic Confirm SO')
    connector_carrier_line_ids = fields.One2many('connector.carrier.line',
                                                 'connector_id',
                                                 string='Carrier Lines')
    get_tax_from_product = fields.Boolean(string='Get Tax from product')
    payment_term_id = fields.Many2one('account.payment.term',
                                      string='Payment Term SO',
                                      help='Payment Term SO'
                                      )
    sale_order_type_b2b_id = fields.Many2one('sale.order.type',
                                             string='Sale Order Type B2B',
                                             required=True,
                                             help='Not in all marketplace we can '
                                                  'separate B2B and B2C.'
                                                  'So, only if possible, '
                                                  'this type is applied ')
    fiscal_position_b2b_id = fields.Many2one('account.fiscal.position',
                                         string='Fiscal Position B2B Order')
    sale_order_type_b2c_id = fields.Many2one('sale.order.type',
                                             required=True,
                                             string='Sale Order Type B2C')
    fiscal_position_id = fields.Many2one('account.fiscal.position',
                                         string='Fiscal Position Order')

    def cron_create_sales_order_connector(self):
        marketplace_ids = self.search([])
        conn_order_model = self.env['connector.order']
        for marketplace in marketplace_ids:
            order_ids = conn_order_model.search([('imported', '=', False),
                                                            ('state', '=', 'ok'),
                                                            ('connector_setting_id', '=', marketplace.id)])
            if order_ids:
                return conn_order_model.import_sale_order(order_ids.filtered(lambda co: not co.sale_id))