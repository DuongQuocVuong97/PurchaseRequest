from datetime import datetime

from odoo import api, fields, models


class RejectReason(models.TransientModel):
    _name = "reject.reason"
    _description = "Reject reason"

    date = fields.Date(default=fields.Date.today(), string="Ngày", required=True)
    reject_reason = fields.Text(string="Lý do", required=True)
    purchase_id = fields.Many2one('purchase.request')

    def action_reject_reason(self):
        active_obj = self.env[self.env.context.get('active_model')].browse(self.env.context.get('active_id'))
        active_obj.write({'state': 'reject'})
        self.purchase_id.write({
            'reason': str(datetime.now()) + ' ' + self.reject_reason
        })
