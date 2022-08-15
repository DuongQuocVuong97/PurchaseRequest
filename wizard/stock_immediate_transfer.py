from odoo import models, fields, api, _
from odoo.exceptions import UserError


class StockImmediateTransfer(models.TransientModel):
    _inherit = 'stock.immediate.transfer'
    _description = 'Immediate Transfer'


class StockBackorderConfirmationInherit(models.TransientModel):
    _inherit = 'stock.backorder.confirmation'

    def process(self):
        res = super().process()
        return res
