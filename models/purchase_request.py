from mock.mock import self

from odoo import models, fields, api
from odoo.exceptions import UserError


class PurchaseRequest(models.Model):
    _name = "purchase.request"
    _description = "Purchase Request"

    name = fields.Text(string="Số phiếu", readonly=True, required=True, copy=False,
                       default=lambda self: self.env['ir.sequence'].next_by_code('purchase.request.sequence'))
    lines = fields.One2many('purchase.request.line', 'requested_id', string='Chi tiết yêu cầu')
    responsible_id = fields.Many2one('res.users', ondelete='set null', string="Responsible", index=True)
    requested_by = fields.Many2one("res.users", string="Người yêu cầu", required=True)
    approver_id = fields.Many2one("res.users", string="Người phê duyệt", required=True)
    department_id = fields.Many2one("hr.department", string="Bộ phận", required=True)
    cost_total = fields.Float(string="Tổng chi phí", compute="_compute_total_amount", readonly=True)
    creation_date = fields.Date(string="Ngày yêu cầu", default=fields.Date.today())
    due_date = fields.Date(string="Ngày cần cấp", default=fields.Date.today())
    approved_date = fields.Date(string="Ngày phê duyệt", default=fields.Date.today())
    company_id = fields.Many2one('res.company', string='Công ty', index=True, default=lambda self: self.env.company.id)
    state = fields.Selection([("draft", "Dự thảo"),
                              ("wait", "Chờ duyệt"),
                              ("approved", "Đã duyệt"),
                              ("done", "Hoàn thành"),
                              ("reject", "Hủy")], default="draft", required=True)
    reason = fields.Text(string="Lý do từ chối duyệt")
    purchase_count = fields.Integer(string="Đơn mua hàng", compute='_compute_purchase_count')
    purchase_order_id = fields.Many2one("purchase.order")
    _sql_constraints = [
        ('name_unique',
         'UNIQUE(name)',
         'The name id must be unique'),
    ]

    @api.onchange('due_date')
    def _onchange_due_date(self):
        if self.due_date:
            for rec in self.lines:
                rec.due_date = self.due_date

    @api.depends("lines")
    def _compute_total_amount(self):
        amount = 0
        for rec in self.lines:
            amount += rec.estimated_subtotal
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

        # tạo đơn po(purchase.order)
        purchase_order = self.env['purchase.order'].create({
            'partner_id': self.requested_by.id,
            'order_line': [(0, 0, {
                'name': 'Test Order',
                'product_id': self.lines.product_id.id,
                'product_qty': self.lines.request_quantity,
                'product_uom': self.lines.product_uom_id.id,
                'price_unit': self.lines.estimated_unit_price,
                'date_planned': self.lines.due_date.strftime('%Y-%m-%d')})],
        })

        self.purchase_order_id = purchase_order.id

    def action_done(self):
        for rec in self:
            rec.state = 'done'

    def action_reject(self):
        return {
            'name': 'Từ chối',
            'domain': [],
            'res_model': 'reject.reason',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'context': {
                'default_purchase_id': self.id
            },
            'target': 'new',
        }

    def _compute_purchase_count(self):
        for rec in self:
            purchase_count = self.env['purchase.request.line'].search_count([('requested_id', '=', rec.id)])
            rec.purchase_count = purchase_count

    def action_count(self):
        return {
            'name': 'Đơn mua hàng',
            'res_model': 'purchase.request.line',
            'type': 'ir.actions.act_window',
            'domain': [('requested_id', '=', self.id)],
            'view_mode': 'tree,form',
            'target': 'current',
        }

    

