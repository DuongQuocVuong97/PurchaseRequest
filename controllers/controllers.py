# -*- coding: utf-8 -*-
# from odoo import http


# class PurchaseLast(http.Controller):
#     @http.route('/purchase_last/purchase_last/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/purchase_last/purchase_last/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('purchase_last.listing', {
#             'root': '/purchase_last/purchase_last',
#             'objects': http.request.env['purchase_last.purchase_last'].search([]),
#         })

#     @http.route('/purchase_last/purchase_last/objects/<model("purchase_last.purchase_last"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('purchase_last.object', {
#             'object': obj
#         })
