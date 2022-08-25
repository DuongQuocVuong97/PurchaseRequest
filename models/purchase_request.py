from odoo import models, fields, api, _
import base64
import datetime
import xlrd

from odoo.exceptions import ValidationError
from odoo.osv import osv


def _check_valid_date(date):
    if date:
        if type(date).__name__ in ['int', 'float']:
            datetime_date = xlrd.xldate_as_datetime(date, 0)
            date_object = datetime_date.date()
        else:
            try:
                date_object = datetime.datetime.strptime(date, '%d/%m/%Y')
            except:
                return None
        return date_object
    return None


def _check_format_excel(file_name):
    if not file_name:
        return False
    if not file_name.endswith('.xls') and not file_name.endswith('.xlsx'):
        return False
    return True


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
    delivered_quantity = fields.Float(string="Số lượng đã đưa", copy=False, readonly=True)
    user_id = fields.Many2one("res.user")
    state = fields.Selection([("draft", "Dự thảo"),
                              ("wait", "Chờ duyệt"),
                              ("approved", "Đã duyệt"),
                              ("done", "Hoàn thành"),
                              ("reject", "Hủy")], default="draft", required=True)
    reason = fields.Text(string="Lý do từ chối duyệt")
    purchase_count = fields.Integer(string="Đơn mua hàng", compute='_compute_purchase_count')
    purchase_order_id = fields.One2many("purchase.order", 'request_id')
    _sql_constraints = [
        ('name_unique',
         'UNIQUE(name)',
         'The name id must be unique'),
    ]

    field_binary_import = fields.Binary(string="Field Binary Import")
    field_binary_name = fields.Char(string="Field Binary Name")

    val_fetch = fields.Text()



    def print_report(self):
        report_id = self.env['purchase.xls'].create({
            'purchase_request_id': self.id
        })
        return {
            'name': 'Báo cáo yêu cầu mua hàng',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'purchase.xls',
            'no_destroy': True,
            'res_id': report_id.id,
            'target': 'new',
            'view_id': self.env.ref('purchaseordered.purchase_xls_wizard_form_view').id
        }

    def action_import(self):
        if not self.field_binary_import:
            raise ValidationError(_("Cảnh báo, bạn phải điền đầy đủ dữ liệu "))
        try:
            if not _check_format_excel(self.field_binary_name):
                raise osv.except_osv("Cảnh báo!",
                                     (
                                         "File không được tìm thấy hoặc không đúng định dạng. Vui lòng kiểm tra lại định dạng file .xls hoặc .xlsx"))
            data = base64.decodestring(self.field_binary_import)
            excel = xlrd.open_workbook(file_contents=data)
            sheet = excel.sheet_by_index(0)
            if not sheet.cell(1, 0).value:
                raise ValidationError(_("Warning!, You must fill data "))

            end = sheet.nrows
            index = 1

            messages = ''
            vals_list = []
            for i in range(index, end):
                product_vals = {}
                product_id = sheet.cell(i, 0).value
                product_uom_id = sheet.cell(i, 1).value
                request_quantity = sheet.cell(i, 2).value
                estimated_unit_price = sheet.cell(i, 4).value
                estimated_subtotal = sheet.cell(i, 5).value
                due_date = sheet.cell(index, 6).value
                note = sheet.cell(index, 7).value

                product = self.env['product.product'].search([('id', '=', int(product_id))], limit=1)
                if not product:
                    messages += _("\n- No Product with code exists %s in row %s.") % (product.name, i)
                uom = self.env['uom.uom'].search([('id', '=', int(product_uom_id))], limit=1)
                if not uom:
                    messages += _("\n- No Unit with code exists %s in row %s.") % (uom.name, i)
                date = _check_valid_date(due_date)
                if messages == '':
                    product_vals = {
                        'requested_id': self.id,
                        'product_id': product.id,
                        'product_uom_id': uom.id,
                        'request_quantity': request_quantity,
                        'estimated_unit_price': estimated_unit_price,
                        'estimated_subtotal': estimated_subtotal,
                        'due_date': date,
                        'description': note,
                    }
                vals_list.append(product_vals)
            if messages or messages != '':
                raise ValidationError(messages)
            self.env['purchase.request.line'].create(vals_list)
            self.field_binary_import = None
            self.field_binary_name = None
        except ValueError as e:
            raise osv.except_osv("Warning!", e)
        except Exception as e:
            raise osv.except_osv("Warning!", e)

    def in_excel(self):
        return self.env.ref('purchaseordered.report_request_xlsx').report_action(self)

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
        vals['user_id'] = self.env.uid
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
            order_vals = {
                'partner_id': rec.requested_by.id,
                'request_id': rec.id
            }
            vals = []
            for line in rec.lines:
                val = {
                    'name': 'Test Order',
                    'product_id': line.product_id.id,
                    'product_qty': line.request_quantity,
                    'product_uom': line.product_uom_id.id,
                    'price_unit': line.estimated_unit_price,
                    'date_planned': line.due_date.strftime('%Y-%m-%d')
                }
                vals.append((0, 0, val))
            order_vals['order_line'] = vals
            rec.env['purchase.order'].create(order_vals)

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
            purchase_count = self.env['purchase.order'].search_count([('request_id', '=', rec.id)])
            rec.purchase_count = purchase_count

    def action_count(self):
        return {
            'name': 'Đơn mua hàng',
            'res_model': 'purchase.order',
            'type': 'ir.actions.act_window',
            'domain': [('id', '=', self.purchase_order_id.id)],
            'view_mode': 'tree,form',
            'target': 'current',
        }


