from odoo import models, fields, api, exceptions
from odoo.exceptions import UserError, ValidationError
import itertools

class CustomProductTemplate(models.Model):
    _inherit = 'product.template'

    width = fields.Char()
    depth = fields.Char()
    height = fields.Char()

    dimension = fields.Char()
    cbm = fields.Char()

    @api.model_create_multi
    def create(self, vals_list):
        templates = super(CustomProductTemplate, self).create(vals_list)
        for template in templates:
            if not template.default_code:
                # Validate the presence of a category and category code
                if not template.categ_id or not template.categ_id.code:
                    raise exceptions.ValidationError(
                        "The product category must have a 'code' to generate a default code."
                    )
                
                category_code = template.categ_id.code

                # Check if the category has a parent and concatenate parent code
                parent_category = template.categ_id.parent_id
                if parent_category and parent_category.code:
                    category_code = f"{parent_category.code}{category_code}"

                # Find existing products with matching category code pattern
                existing_products = self.search(
                    [('default_code', 'like', f"{category_code}-%")]
                )

                # Determine the highest number from existing product codes
                last_number = 0
                for product in existing_products:
                    parts = product.default_code.split('-')
                    if len(parts) > 1 and parts[1].isdigit():
                        number = int(parts[1])
                        last_number = max(last_number, number)

                # Assign the new default code
                template.default_code = f"{category_code}-{last_number + 1}"

        return templates

from itertools import product as itertools_product

class CustomProductProduct(models.Model):
    _inherit = 'product.product'

    width = fields.Char()
    depth = fields.Char()
    height = fields.Char()

    dimension = fields.Char()
    cbm = fields.Char()

    default_code = fields.Char(readonly=True)

    @api.model_create_multi
    def create(self, vals_list):
        products = super(CustomProductProduct, self).create(vals_list)
        for variant in products:
            if not variant.default_code:
                template = variant.product_tmpl_id

                # Generate template default_code if it doesn't exist
                if not template.default_code:
                    if not template.categ_id or not template.categ_id.code:
                        raise exceptions.ValidationError(
                            "The product category must have a 'code' to generate a default code."
                        )

                    category_code = template.categ_id.code

                    # Check if the category has a parent and concatenate parent code
                    parent_category = template.categ_id.parent_id
                    if parent_category and parent_category.code:
                        category_code = f"{parent_category.code}{category_code}"

                    existing_templates = self.env['product.template'].search(
                        [('default_code', 'like', f"{category_code}-%")]
                    )

                    # Determine the highest numbering
                    last_number = 0
                    for existing_template in existing_templates:
                        parts = existing_template.default_code.split('-')
                        if len(parts) > 1 and parts[1].isdigit():
                            number = int(parts[1])
                            last_number = max(last_number, number)

                    # Generate template default_code
                    template.default_code = f"{category_code}-{last_number + 1}"

                # Generate variant codes based on attribute values
                attribute_values = variant.product_template_attribute_value_ids
                if attribute_values:
                    # Group attribute values by attribute
                    attribute_groups = {}
                    for av in attribute_values:
                        attribute_groups.setdefault(av.attribute_id.id, []).append(av.name)

                    # Generate all combinations of attribute values
                    attribute_combinations = list(itertools_product(
                        *[attribute_groups[attr_id] for attr_id in attribute_groups]
                    ))

                    # Generate variant codes for each combination
                    for combination in attribute_combinations:
                        short_codes = [''.join(word[:2].upper() for word in value.split()) for value in combination]
                        variant_code = '-'.join(short_codes)

                        # Combine with template.default_code
                        base_default_code = f"{template.default_code}-{variant_code}"

                        # Ensure uniqueness
                        unique_code = base_default_code
                        suffix = 1
                        while self.search([('default_code', '=', unique_code)], limit=1):
                            unique_code = f"{base_default_code}-{suffix}"
                            suffix += 1

                        variant.default_code = unique_code
                else:
                    # No attributes: use the template default_code
                    variant.default_code = template.default_code

        return products