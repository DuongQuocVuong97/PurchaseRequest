from odoo import models, fields, api
from odoo.exceptions import UserError


class PurchaseRequest(models.Model):
    _name = "purchase.request"
    _description = "Purchase Request"

    name = fields.Text(string="Số phiếu", readonly=True, required=True, copy=False,
                       default=lambda self: self.env['ir.sequence'].next_by_code('purchase.request.sequence'))
    requested_by = fields.Many2one("res.user", string="Người yêu cầu", required=True)
    department_id = fields.Many2one("hr.department", string="Bộ phận", required=True)
    cost_total = fields.Float(string="Tổng chi phí", readonly=True)
    creation_date = fields.Date(string="Ngày yêu cầu", default=fields.Date.today())
    due_date = fields.Date(string="Ngày cần cấp")
    approved_date = fields.Date(string="Ngày phê duyệt")
    company_id = fields.Many2one("res.company", string="Công ty", readonly=True)
    state = fields.Selection([("draft", "Draft"),
                              ("wait", "Wait"),
                              ("approved", "Approved"),
                              ("done", "Done"),
                              ("reject", "Reject")], default="draft", required=True)

    _sql_constraints = [
        ('name_unique',
         'UNIQUE(name)',
         'The name id must be unique'),
    ]

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

    def write(self, vals):
        if any(state == 'wait' or 'approved' or 'reject' for state in set(self.mapped('state'))):
            raise UserError("Không được sửa thông tin")
        else:
            return super().write(vals)
