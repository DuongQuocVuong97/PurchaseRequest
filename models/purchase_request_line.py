from odoo import models, fields, api

class PurchaseRequestLine(models.Model):
    _name = "purchase.request.line"
    _description = "Purchase Request Line"

    product_id = fields.Many2one("product.template", string="Sản phẩm", required=True)
    product_uom_id = fields.Many2one("product.uom", string="Đơn vị tính", readonly=True)
    request_quantity = fields.Float(string="Số lượng yêu cầu", required=True)
    estimated_unit_price = fields.Float(string="Đơn giá dự kiến")
    estimated_subtotal = fields.Float(string="Chi phí dự kiến", compute="_compute_total")
    due_date = fields.Date(string="Ngày cần cấp", default=fields.Date.today(), required=True)
    description = fields.Text(string="Ghi chú")
    delivered_quantity = fields.Float(string="Số lượng đã mua")
