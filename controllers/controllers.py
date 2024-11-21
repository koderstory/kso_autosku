# -*- coding: utf-8 -*-
# from odoo import http


# class KoderstoryDynamicCode(http.Controller):
#     @http.route('/koderstory_dynamic_code/koderstory_dynamic_code', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/koderstory_dynamic_code/koderstory_dynamic_code/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('koderstory_dynamic_code.listing', {
#             'root': '/koderstory_dynamic_code/koderstory_dynamic_code',
#             'objects': http.request.env['koderstory_dynamic_code.koderstory_dynamic_code'].search([]),
#         })

#     @http.route('/koderstory_dynamic_code/koderstory_dynamic_code/objects/<model("koderstory_dynamic_code.koderstory_dynamic_code"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('koderstory_dynamic_code.object', {
#             'object': obj
#         })

