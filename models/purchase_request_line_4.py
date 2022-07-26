from odoo import models, fields, api


class PurchaseRequestLine4(models.Model):
    _name = "purchase.request.line.4"
    _description = "Purchase Request Line"

    product_id = fields.Many2one("product.template", string="Sản phẩm", required=True)
    purchase_line_id = fields.Many2one("purchase.request.4", required=True, index=True)
    product_uom_id = fields.Many2one("uom.uom", string="Đơn vị tính", readonly=True)
    request_quantity = fields.Integer(string="Số lượng yêu cầu", required=True)
    estimated_unit_price = fields.Float(string="Đơn giá dự kiến")
    estimated_subtotal = fields.Float(string="Chi phí dự kiến", compute="_compute_total")
    due_date = fields.Date(string="Ngày cần cấp", default=fields.Date.today(), required=True)
    description = fields.Text(string="Ghi chú")
    delivered_quantity = fields.Float(string="Số lượng đã mua")

    @api.depends("request_quantity", "estimated_unit_price")
    def _compute_total(self):
        for r in self:
            r.estimated_subtotal = r.request_quantity * r.estimated_unit_price
