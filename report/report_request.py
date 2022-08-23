from docutils.nodes import row
from xlsxwriter import worksheet

from odoo import models


class PartnerXlsx(models.AbstractModel):
    _name = 'report.purchaseordered.request_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, partners):
        for obj in partners:
            report_name = obj.name
            state = obj.state
            wait_trans = "Chờ duyệt"
            approved_trans = "Đã duyệt"
            done_trans = "Hoàn thành"
            query = '''
                select prl.id, pp.default_code, prl.request_quantity
                from purchase_request_line prl
                inner join product_product pp on pp.id = prl.product_id
            '''
            self._cr.execute(query)
            # One sheet by partner
            sheet = workbook.add_worksheet(report_name[:31])
            center_noborder = workbook.add_format({
                'align': 'center',
                'valign': 'vcenter',
            })
            bold = workbook.add_format({'bold': 1,
                                        'align': 'center',
                                        'valign': 'vcenter',
                                        })
            center = workbook.add_format({'border': 1,
                                          'align': 'center',
                                          'valign': 'vcenter',
                                          })
            center_format = workbook.add_format({
                'bold': 1,
                'border': 1,
                'align': 'center',
                'valign': 'vcenter',
            })
            center_format.set_center_across()
            sheet.set_column('A:J', 30)
            sheet.set_row(0, 15)
            sheet.set_row(1, 30)
            sheet.merge_range('C1:G1', 'Nhà máy sản xuất Kangaroo', center_format)
            sheet.merge_range('A2:G2', 'BÁO CÁO YÊU CẦU MUA HÀNG', center_format)
            sheet.merge_range('E3:F3', 'Người yêu cầu', bold)
            sheet.write(2, 6, obj.requested_by.name, center_noborder)
            sheet.merge_range('E4:F4', 'Từ ngày', bold)
            sheet.write(3, 6, obj.creation_date.strftime('%D-%M-%Y'), center_noborder)
            sheet.merge_range('E5:F5', 'Đến ngày', bold)
            sheet.write(4, 6, obj.due_date.strftime('%D-%M-%Y'), center_noborder)
            sheet.merge_range('E6:F6', 'Trạng thái', bold)
            if state == 'approved':
                sheet.write(5, 6, approved_trans, center_noborder)
            elif state == 'done':
                sheet.write(5, 6, done_trans, center_noborder)
            elif state == 'wait':
                sheet.write(5, 6, wait_trans, center_noborder)
            sheet.write(7, 0, 'STT', center_format)
            sheet.write(7, 1, 'Mã sản phẩm', center_format)
            sheet.write(7, 2, 'Sản phẩm', center_format)
            sheet.write(7, 3, 'Đơn vị tính', center_format)
            sheet.write(7, 4, 'Số lượng yêu cầu', center_format)
            sheet.write(7, 5, 'Số lượng đáp ứng', center_format)
            sheet.write(7, 6, 'Đơn giá dự kiến', center_format)
            sheet.write(7, 7, 'Chi phí dự kiến', center_format)
            sheet.write(7, 8, 'Ghi chú', center_format)
            sheet.write(7, 9, 'Yêu cầu mua hàng', center_format)
            sheet.write(8, 9, obj.name, center_format)
            i = 8
            k = 14
            n = 1
            sum_request_quantity = 0
            sum_delivered_quantity = 0

            for line in partners.lines:
                sum_request_quantity += line.request_quantity
                sum_delivered_quantity += line.delivered_quantity
                sheet.write(i, 0, n, center)
                sheet.write(i, 1, line.product_id.id, center)
                sheet.write(i, 2, line.product_id.name, center)
                sheet.write(i, 3, line.product_uom_id.name, center)
                sheet.write(i, 4, line.request_quantity, center)
                sheet.write(i, 5, line.delivered_quantity, center)
                sheet.write(i, 6, line.estimated_unit_price, center)
                sheet.write(i, 7, line.estimated_subtotal, center)
                sheet.write(i, 8, str(line.description), center)
                sheet.write(i + 1, 3, 'Tổng cộng', center_format)
                sheet.write(i + 1, 4, sum_request_quantity, center_format)
                sheet.write(i + 1, 5, sum_delivered_quantity, center_format)
                sheet.write(k, 3, 'Quản lý Cửa hàng/Kho tổng', bold)
                sheet.write(k + 1, 3, '(Ký,ghi rõ họ tên)', center_noborder)
                sheet.write(k, 6, 'Lập phiếu', bold)
                sheet.write(k + 1, 6, '(Ký,ghi rõ họ tên)', center_noborder)
                n += 1
                i += 1
