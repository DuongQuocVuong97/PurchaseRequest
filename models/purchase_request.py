from odoo import models, fields, api
from odoo.exceptions import UserError


class PurchaseRequest(models.Model):
    _name = "purchase.request"
    _description = "Purchase Request"

    name = fields.Text(string="Số phiếu", readonly=True, required=True, copy=False,
                       default=lambda self: self.env['ir.sequence'].next_by_code('purchase.request.sequence'))
    lines = fields.One2many('purchase.request.line', 'requested_id', string='Chi tiết yêu cầu')
    requested_by = fields.Many2one("res.users", string="Người yêu cầu", required=True)
    approver_id = fields.Many2one("res.users", string="Người phê duyệt", required=True)
    department_id = fields.Many2one("hr.department", string="Bộ phận", required=True)
    cost_total = fields.Float(string="Tổng chi phí", compute="_compute_total_amount", readonly=True)
    creation_date = fields.Date(string="Ngày yêu cầu", default=fields.Date.today())
    due_date = fields.Date(string="Ngày cần cấp")
    approved_date = fields.Date(string="Ngày phê duyệt")
    company_id = fields.Many2one('res.company', string='Công ty', index=True, default=lambda self: self.env.company.id)
    state = fields.Selection([("draft", "Dự thảo"),
                              ("wait", "Chờ duyệt"),
                              ("approved", "Đã duyệt"),
                              ("done", "Hoàn thành"),
                              ("reject", "Hủy")], default="draft", required=True)
    reason_id = fields.Many2one('reject.reason')
    _sql_constraints = [
        ('name_unique',
         'UNIQUE(name)',
         'The name id must be unique'),
    ]

    @api.depends("lines")
    def _compute_total_amount(self):
        amount = 0
        for r in self.lines:
            amount += r.estimated_subtotal
        self.cost_total = amount

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('purchase.request.sequence') or 'New'
        result = super(PurchaseRequest, self).create(vals)
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
