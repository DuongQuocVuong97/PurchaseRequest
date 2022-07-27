# -*- coding: utf-8 -*-
# from odoo import http


# class Purchasehomework(http.Controller):
#     @http.route('/purchasehomework/purchasehomework/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/purchasehomework/purchasehomework/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('purchasehomework.listing', {
#             'root': '/purchasehomework/purchasehomework',
#             'objects': http.request.env['purchasehomework.purchasehomework'].search([]),
#         })

#     @http.route('/purchasehomework/purchasehomework/objects/<model("purchasehomework.purchasehomework"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('purchasehomework.object', {
#             'object': obj
#         })
