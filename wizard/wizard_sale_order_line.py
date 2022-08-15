import base64
import tempfile
from datetime import date, datetime
import re

import xlsxwriter

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class ImportPurchaseRequestLine(models.TransientModel):
    _name = 'import.purchase.request.line'

    import_date = fields.Date(required=False, default=date.today(), string='Ngày Nhập')
    template_file_url_default = fields.Char(default=lambda self: self.env['ir.config_parameter'].sudo().get_param(
        'web.base.url') + '/z_com_import_sale_order/static/Template_import_danh_sach_don_hang_ban.xls',
                                            string='Template File URL')
    order_id = fields.Many2one('sale.order')
    error_message = fields.Text()
    datas = fields.Binary

    def action_button_ok(self):
        self.ensure_one()
        return {'type': 'ir.actions.act_window_close'}

    def action_import_so_line(self):
        self.ensure_one()
        data = self.datas
        sheet = False

        user = self.env.user
        path = '/wizard_import_sale_order_template_' + user.login + '_' + str(self[0].id) + '_' + str(
            datetime.now()).replace(":", '_') + '.xls'
        path = path.replace(' ', '_')

        read_excel_obj = self.env['read.excel']
        excel_data = read_excel_obj.read_file(data, sheet, path)
        if len(excel_data[0]) < 5:
            raise ValidationError(_('File excel phải có ít nhất 5 cột'))
        if len(excel_data) < 2:
            raise ValidationError(_('File excel phải có ít nhất 1 hàng sau header'))
        excel_data = excel_data[1:]
        row_number = 2
        dict_error = dict()
        for row in excel_data:
            value = {'order_id': self.order_id.id}
            space = len('Hàng {}: '.format(row_number)) + 8
            product = ''
            if not row[0]:
                dict_error.update({row_number: _('- Bạn phải nhập mã sản phẩm\n') + ' ' * space})
            else:
                product = self.env['product.product'].search([('default_code', '=', str(row[0]).strip())])
                if product:
                    if row[1]:
                        name = str(row[1])
                    else:
                        name = '[{}] {}'.format(product.default_code, product.name)
                    value.update({'product_id': product[0].id, 'name': name, 'product_uom': product[0].uom_id.id})
                else:
                    dict_error.update({row_number: dict_error.get(row_number, '') + '-' + _(
                        'Không thể tìm thấy sản phẩm với mã {} trong hệ thống\n').format(row[0]) + ' ' * space})

            if row[2]:
                try:
                    row[2] = str(row[2]).replace(',', '.')
                    f = float(row[2])
                    if f <= 0:
                        dict_error.update({row_number: dict_error.get(row_number, '') + '-' + _(
                            'Số lượng đặc hàng sai định dạng\n') + ' ' * space})
                    else:
                        value.update({'product_uom_qty': f})
                except:
                    dict_error.update({row_number: dict_error.get(row_number, '') + _(
                        'Bạn phải nhập số lượng đặt hàng\n') + ' ' * space})

            else:
                dict_error.update({row_number: dict_error.get(row_number, '') + '-' + _(
                    'Bạn phải nhập số lượng đặt hàng\n') + ' ' * space})
            if row[4]:
                try:
                    row[4] = str(row[4]).replace(',', '.')
                    f = float(row[4])
                    if f < 0:
                        dict_error.update({row_number: dict_error.get(row_number, '') + '-' + _(
                            'Chiết khấu phải lớn hơn 0\n') + ' ' * space})
                    else:
                        value.update({'discount': f})
                except:
                    dict_error.update({row_number: dict_error.get(row_number, '') + '-' + _(
                        ' Chiết khấu sai định dạng\n') + ' ' * space})
            if row[5]:
                try:
                    row[5] = str(row[5]).replace(',', '.')
                    f = float(row[5])
                    if f < 0:
                        dict_error.update({row_number: dict_error.get(row_number, '') + '-' + _(
                            'Thời gian giao hàng phải lớn hơn 0 \n') + ' ' * space})
                    else:
                        value.update({'customer_lead': f})
                except:
                    dict_error.update({row_number: dict_error.get(row_number, '') + '-' + _(
                        'Thời gian giao hàng sai định dạng\n') + ' ' * space})

            if row_number not in dict_error:
                order_line = ''
                try:
                    order_line = self.env['sale.order.line'].create(value)
                except Exception as e:
                    dict_error.update(
                        {row_number: dict_error.get(row_number, '') + '-' + _(' {}\n'.format(e)) + ' ' * space})
                if order_line:
                    if order_line.order_id.pricelist_id and order_line.order_id.partner_id:
                        order_line.product_uom_change()
                    else:
                        order_line.write({'price_unit': product.lst_price})
            row_number += 1
        if dict_error:
            fileobj_or_path = tempfile.gettempdir() + path
            wb = xlsxwriter.Workbook(fileobj_or_path)
            ws = wb.add_worksheet()
            table_header = wb.add_format({
                'bold': 1,
                'text_wrap': True,
                'align': 'center',
                'valign': 'vcenter',
                'border': 1,
                'font_name': 'Times New Roman',
                'font_size': 11,
            })
            table_header_error = wb.add_format({
                'bold': 1,
                'text_wrap': True,
                'align': 'center',
                'valign': 'vcenter',
                'border': 1,
                'font_name': 'Times New Roman',
                'font_size': 11,
                'bg_color': '#FFC7CE'
            })
            row_default_left = wb.add_format({
                'text_wrap': True,
                'align': 'left',
                'valign': 'vcenter',
                'font_name': 'Times New Roman',
                'border': 1,
                'font_size': 11,
            })
            row_default_left_error = wb.add_format({
                'text_wrap': True,
                'align': 'left',
                'valign': 'vcenter',
                'font_name': 'Times New Roman',
                'border': 1,
                'font_size': 11,
                'bg_color': '#FFC7CE'
            })
            ws.set_column('A:A', 15)
            ws.set_column('B:B', 15)
            ws.set_column('C:C', 15)
            ws.set_column('D:D', 15)
            ws.set_column('E:E', 15)
            ws.set_column('F:F', 100)
            ws.write('A1', 'Mã sản phẩm', table_header)
            ws.write('B1', 'Miêu tả', table_header)
            ws.write('C1', 'Số lượng đặt hàng', table_header)
            ws.write('D1', 'Tỷ lệ CK (%)', table_header)
            ws.write('E1', 'Thời gian giao hàng', table_header)
            ws.write('F1', 'Chi tiết lỗi', table_header_error)
            row = 2
            message = ''
            for i in dict_error:
                message += 'Hàng {} : {}'.format(i, dict_error[i]) + '\n'
                ws.write('A{}'.format(row), excel_data[(i - 2)][0], row_default_left)
                ws.write('B{}'.format(row), excel_data[(i - 2)][1], row_default_left)
                ws.write('C{}'.format(row), excel_data[(i - 2)][2], row_default_left)
                ws.write('D{}'.format(row), excel_data[(i - 2)][3], row_default_left)
                ws.write('E{}'.format(row), excel_data[(i - 2)][4], row_default_left)
                ws.write('F{}'.format(row), re.sub(' +', ' ', dict_error[i].replace('\n', '')).replace(' -', ','),
                         row_default_left_error)
                row += 1
            wb.close()
            self.write({'error_message': _(message)})
            f = open(fileobj_or_path, "rb")
            data = f.read()
            xlsx_data = base64.b64encode(data)
            self.attachment_id.write({
                'datas': xlsx_data,
            })
            return {
                'name': _('Warning'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'wizard.import.sale.order.line',
                'no_destroy': True,
                'res_id': self.id,
                'target': 'new',
                'view_id': self.env.ref(
                    'z_com_import_sale_order.wizard_import_sale_order_line_view_form_warning') and self.env.ref(
                    'z_com_import_sale_order.wizard_import_sale_order_line_view_form_warning').id or False,
            }
