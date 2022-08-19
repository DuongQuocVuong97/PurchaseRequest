from odoo import models, fields, api, _
from odoo.exceptions import UserError


class StockImmediateTransfer(models.TransientModel):
    _inherit = 'stock.immediate.transfer'
    _description = 'Immediate Transfer'


class StockBackorderConfirmationInherit(models.TransientModel):
    _inherit = 'stock.backorder.confirmation'
    array_dict = []
    this_dict = {}

    def process(self):
        res = super().process()
        purchase_order_id = self._context.get('active_id')
        purchase_request = self.env['purchase.request'].search([('purchase_order_id', '=', purchase_order_id)])
        array_dict = []
        for line in self.pick_ids.move_line_ids_without_package:
            this_dict = {}
            this_dict['product_id'] = line.product_id.id
            this_dict['delivered_quantity'] = line.qty_done
            array_dict.append(this_dict)
        for line in purchase_request.lines:
            for secline in array_dict:
                if secline['product_id'] == line.product_id.id:
                    line.delivered_quantity += secline.get('delivered_quantity')
        return res
