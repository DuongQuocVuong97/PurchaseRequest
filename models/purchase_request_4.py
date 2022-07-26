from odoo import models, fields, api
from odoo.exceptions import UserError


class PurchaseRequest4(models.Model):
    _name = "purchase.request.4"
    _description = "Purchase Request"

    name = fields.Text(string="Số phiếu", readonly=True, required=True, copy=False,
                       default=lambda self: self.env['ir.sequence'].next_by_code('purchase.request.4.sequence'))
    request_ids = fields.One2many("purchase.request.line.4", "purchase_line_id", string="ID")
    requested_by = fields.Many2one("res.users", string="Người yêu cầu", required=True)
    approver_id = fields.Many2one("res.users", string="Người phê duyệt", required=True)
    department_id = fields.Many2one("hr.department", string="Bộ phận", required=True)
    cost_total = fields.Float(string="Tổng chi phí", readonly=True)
    creation_date = fields.Date(string="Ngày yêu cầu", default=fields.Date.today())
    due_date = fields.Date(string="Ngày cần cấp")
    approved_date = fields.Date(string="Ngày phê duyệt")
    company_id = fields.Many2one("res.company", string="Công ty", readonly=True)
    state = fields.Selection([("draft", "Dự thảo"),
                              ("wait", "Chờ duyệt"),
                              ("approved", "Đã duyệt"),
                              ("done", "Hoàn thành"),
                              ("reject", "Hủy")], default="draft", required=True)

    _sql_constraints = [
        ('name_unique',
         'UNIQUE(name)',
         'The name id must be unique'),
    ]

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('purchase.request.4.sequence') or 'New'
        result = super(PurchaseRequest4, self).create(vals)
        return result

    def action_draft(self):
        for rec in self:
            rec.state = 'draft'

    def action_wait(self):
        for rec in self:
            rec.state = 'wait'

    def action_approved(self):
        for rec in self:
            rec.state = 'approved'

    def action_done(self):
        for rec in self:
            rec.state = 'done'

    def action_reject(self):
        for rec in self:
            rec.state = 'reject'

    def write(self, vals):
        if any(state == 'wait' or 'approved' for state in set(self.mapped('state'))):
            raise UserError("Không được sửa thông tin")
        else:
            return super().write(vals)
