from odoo import models


class PartnerXlsx(models.AbstractModel):
    _name = 'report.purchaseordered.request_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, partners):
        for obj in partners:
            report_name = obj.name
            # One sheet by partner
            sheet = workbook.add_worksheet(report_name[:31])
            bold = workbook.add_format({'bold': True})
            sheet.write(0, 0, obj.name, bold)
            sheet.write(1, 0, 'Sản phẩm')
            sheet.write(1, 1, 'Đơn vị tính')
            sheet.write(1, 2, 'Số lượng yêu cầu')
            sheet.write(1, 3, 'Đơn giá dự kiến')
            sheet.write(1, 4, 'Chi phí dự kiến')
            sheet.write(1, 5, 'Ngày cần cấp')
            sheet.write(1, 6, 'Ghi chú')

            i = 2
            for line in partners.lines:
                sheet.write(i, 0, line.product_id.name)
                sheet.write(i, 1, line.product_uom_id.name)
                sheet.write(i, 2, line.request_quantity)
                sheet.write(i, 3, line.estimated_unit_price)
                sheet.write(i, 4, line.estimated_subtotal)
                sheet.write(i, 5, line.due_date.strftime('%D-%M-%Y'))
                sheet.write(i, 6, str(line.description))
                i += 1
