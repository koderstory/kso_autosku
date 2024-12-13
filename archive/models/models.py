# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ProductCategory(models.Model):
    _inherit = 'product.category'
    code = fields.Char(
        string="Category Code", 
        store=True, 
        help="Unique code for the product category", 
        index=True)

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    dimension = fields.Char(string='Dimension')
    width = fields.Char(string='Width')
    depth = fields.Char(string='Depth')
    height = fields.Char(string='Height')
    cbm = fields.Char(string='CBM')

    @api.constrains('categ_id')
    def _check_category_code(self):
        for product in self:
            # Ensure the product has a category
            if product.categ_id and not product.categ_id.code:
                raise ValidationError(
                    "The product category must have a code before saving the product."
                )


    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            
            # Check category, does it have code
            category = self.env['product.category'].browse(vals.get('categ_id'))
            if category and not category.code:
                raise ValidationError(
                    "The product category must have a code before creating the product."
                )

            # Ensure the category exists and has a code
            if not vals.get('default_code'):
                category = self.env['product.category'].browse(vals.get('categ_id'))

                # Check if the category has a code, if not, skip generating default_code
                if category and category.code:
                    category_code = category.code

                    # Find the existing products in the same category to determine the next number
                    existing_products_in_category = self.search([
                        ('categ_id', '=', category.id),
                        ('default_code', 'ilike', category_code + '%')
                    ])

                    # Determine the next number for this category
                    next_number = len(existing_products_in_category) + 1

                    # Generate the default_code in the format 'CategoryCode-Number'
                    vals['default_code'] = f"{category_code}-{next_number}"
            # vals['default_code'] = '1000'

        # Call the parent class' create method with the updated vals_list
        return super(ProductTemplate, self).create(vals_list)


    def write(self, vals):
        # Check if the category is being updated and validate the code
        if 'categ_id' in vals:
            category = self.env['product.category'].browse(vals['categ_id'])
            if category and not category.code:
                raise ValidationError(
                    "The product category must have a code before updating the product."
                )
        # Proceed with the update
        return super(ProductTemplate, self).write(vals)
