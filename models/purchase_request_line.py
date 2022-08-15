from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class PurchaseRequestLine(models.Model):
    _name = "purchase.request.line"
    _description = "Purchase Request Line"

    product_id = fields.Many2one("product.product", string="Sản phẩm", required=True)
    requested_id = fields.Many2one("purchase.request")
    product_uom_id = fields.Many2one("uom.uom", related='product_id.uom_id', string="Đơn vị tính")
    request_quantity = fields.Integer(string="Số lượng yêu cầu", required=True)
    estimated_unit_price = fields.Float(string="Đơn giá dự kiến")
    estimated_subtotal = fields.Float(string="Chi phí dự kiến", compute="_compute_total", readonly=True)
    due_date = fields.Date(string="Ngày cần cấp", required=True, default=fields.Date.today())
    description = fields.Text(string="Ghi chú")
    delivered_quantity = fields.Float(string="Số lượng đã đưa", copy=False, compute="_compute_delivered_quantity")

    @api.depends("request_quantity", "estimated_unit_price")
    def _compute_total(self):
        for r in self:
            r.estimated_subtotal = r.request_quantity * r.estimated_unit_price

    @api.constrains('request_quantity')
    def _check_request_quantity(self):
        for rc in self:
            if rc.request_quantity <= 0:
                raise ValidationError(_('You cannot create recursive departments.'))


