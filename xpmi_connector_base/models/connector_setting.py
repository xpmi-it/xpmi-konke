# -*- coding: utf-8 -*-
# Copyright (C) 2023-Today:
#     Dinamiche Aziendali srl (<http://www.dinamicheaziendali.it/>)
# @author: Gianmarco Conte (gconte@dinamicheaziendali.it)
# License GPL-3.0 or later (http://www.gnu.org/licenses/gpl.html).
from odoo import fields, models, api
import requests

MAGIC_FIELDS = list(models.MAGIC_COLUMNS)
if hasattr(models.BaseModel, "CONCURRENCY_CHECK_FIELD"):
    MAGIC_FIELDS.append(models.BaseModel.CONCURRENCY_CHECK_FIELD)
else:
    MAGIC_FIELDS.append("__last_update")
domain_fields = """[("name", "not in", %s), ("ttype", "not in", ["reference", "function"]), ("model_id", "=", 'product.product'),]""" % str(
    MAGIC_FIELDS)


class ConnectorSetting(models.Model):
    _name = 'connector.setting'
    _description = 'Connector Setting'

    @api.model
    def _lang_get(self):
        return self.env['res.lang'].get_installed()

    name = fields.Char(string='Name')
    marketplace = fields.Selection([], string='Marketplace')
    user = fields.Char(string='User', required=True)
    passwd = fields.Char(string='Passwd', required=True)
    sale_order_team_id = fields.Many2one('crm.team', string='Sale Team')
    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse', required=True)
    pricelist_id = fields.Many2one('product.pricelist', string='Pricelist',
                                   required=True)
    lang = fields.Selection(_lang_get, string='Language')
    mapping_product = fields.Many2one("ir.model.fields",
                                      ondelete="cascade",
                                      string="Mapping Product",
                                      required=True,
                                      domain=domain_fields)

    send_pricelist = fields.Selection([('sftp', 'Sftp')],
                                      string='Send Pricelist')
    pricelist_user_sftp = fields.Char(string='Pricelist User Sftp')
    pricelist_pwd_sftp = fields.Char(string='Pricelist Pwd Sftp')
    pricelist_port_sftp = fields.Char(string='Pricelist Port Sftp')
    pricelist_ip_sftp = fields.Char(string='Url Sftp')
    pricelist_file_name = fields.Char(string='Filename Pricelist')
    pricelist_file_path_sftp = fields.Char(string='Path Sftp')
    pricelist_file = fields.Binary(string='Pricelist File', readonly=True,
                                   help="File Pricelist",
                                   copy=False)
    country_id = fields.Many2one('res.country', string='Country', required=True)
