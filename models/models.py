# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class purchase2(models.Model):
#     _name = 'purchase2.purchase2'
#     _description = 'purchase2.purchase2'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
