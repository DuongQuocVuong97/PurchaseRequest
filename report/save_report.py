from odoo import models, fields


class SaveReport(models.Model):
    _name = 'save.report'

    requested_id = fields.Many2one("purchase.request", string="Đơn yêu cầu")
    requested_by = fields.Many2one("res.users", string="Người yêu cầu", required=True)
    product_id = fields.Many2one("product.product", string="Sản phẩm", required=True)
    creation_date = fields.Date(string="Ngày yêu cầu", default=fields.Date.today())
    due_date = fields.Date(string="Ngày cần cấp", required=True, default=fields.Date.today())
    request_quantity = fields.Integer(string="Số lượng yêu cầu", required=True)
    delivered_quantity = fields.Float(string="Số lượng đã đưa", copy=False, readonly=True)
    estimated_unit_price = fields.Float(string="Đơn giá dự kiến")

    def create(self, values):
        """select prl.requested_id, pr.requested_by, prl.product_id, pr.creation_date,
           pr.due_date, prl.request_quantity,prl.delivered_quantity, prl.estimated_unit_price
           from purchase_request_line prl
           inner join purchase_request pr
           ON prl.requested_id = pr.id
           Where pr.creation_date between %s AND %s"""

        return super(self).create(values)


