from odoo import api, fields, models, _


class PurchaseExcel(models.TransientModel):
    _name = 'purchase.xls'
    _description = 'Purchase Excel'

    creation_date = fields.Date(string="Từ ngày", default=fields.Date.today())
    due_date = fields.Date(string="Đến ngày", default=fields.Date.today())
    purchase_request_id = fields.Many2one('purchase.request')

    def print_report(self):
        self.env.cr.execute(f"""select prl.requested_id, pr.requested_by, prl.product_id, pr.creation_date,
                                pr.due_date, prl.request_quantity,prl.delivered_quantity, prl.estimated_unit_price 
                                from purchase_request_line prl
                                inner join purchase_request pr
                                ON prl.requested_id = pr.id
                                Where pr.creation_date between %s AND %s """, (self.creation_date, self.due_date))
        vals = self._cr.fetchall()
        for val in vals:
            val.create({

            })
        return {
            'type': 'ir.actions.act_url',
            'url': ('/report/xlsx/purchaseordered.report_request_stat_xlsx/%s' % self.id),
            'target': 'new',
            'res_id': self.id,
        }
        # self.purchase_request_id.write({
        #     'val_fetch': vals
        # })
        #
        # return self.env.ref('purchaseordered.report_request_stat_xlsx').report_action(self.purchase_request_id)




        #Vals xem nó là gì rồi import dữ liệu vào excel
        # return {
        #     'name': _('Báo cáo yêu cầu mua hàng'),
        #     'res_model': 'purchase.request.line',
        #     'view_mode': 'tree',
        #     'view_ids': [(4, self.env.ref('purchaseordered.purchase.request.line').id)]
        #     'domain': [('requested_id', '=',)]
        #
        # }

        # return self.env.ref('purchaseordered.report_request_xlsx').report_action(self.purchase_request_id)
