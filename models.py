from odoo import models,fields


class CustomProductTemplate(models.Model):
    _inherit = 'product.template'

    width = fields.Char()
    depth = fields.Char()
    height = fields.Char()

    dimension = fields.Char()
    cbm = fields.Char()


class CustomProductProduct(models.Model):
    _inherit = 'product.product'

    width = fields.Char()
    depth = fields.Char()
    height = fields.Char()

    dimension = fields.Char()
    cbm = fields.Char()


