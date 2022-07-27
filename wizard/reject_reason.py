from odoo import api, fields, models

class RejectReason(models.TransientModel):
    _name = "reject.reason"
    _description = "Reject reason"

    date = fields.Date(default=fields.Date.today(), string="Ngày", required=True)
    reject_reason = fields.Text(string="Lý do", required=True)
