# -*- coding: utf-8 -*-
# from odoo import http


# class Purchase(http.Controller):
#     @http.route('/purchase/purchase/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/purchase/purchase/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('purchase.listing', {
#             'root': '/purchase/purchase',
#             'objects': http.request.env['purchase.purchase'].search([]),
#         })

#     @http.route('/purchase/purchase/objects/<model("purchase.purchase"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('purchase.object', {
#             'object': obj
#         })
