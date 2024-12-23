from odoo import models, fields, api, exceptions


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
                # Check if the category has a code
                if not template.categ_id or not template.categ_id.code:
                    raise exceptions.ValidationError(
                        "The product category must have a 'code' to generate a default code."
                    )

                category_code = template.categ_id.code

                # Find all existing products with matching category code
                existing_products = self.search(
                    [('default_code', 'like', f"{category_code}-%")]
                )

                # Determine the highest numbering
                last_number = 0
                for product in existing_products:
                    parts = product.default_code.split('-')
                    if len(parts) > 1 and parts[1].isdigit():
                        number = int(parts[1])
                        last_number = max(last_number, number)

                # Start numbering from 1 if no valid existing product
                template.default_code = f"{category_code}-{last_number + 1}"
        return templates


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
        for product in products:
            if not product.default_code:
                template = product.product_tmpl_id

                # Generate template default_code if it doesn't exist
                if not template.default_code:
                    if not template.categ_id or not template.categ_id.code:
                        raise exceptions.ValidationError(
                            "The product category must have a 'code' to generate a default code."
                        )

                    category_code = template.categ_id.code
                    existing_products = template.search(
                        [('default_code', 'like', f"{category_code}-%")]
                    )

                    # Determine the highest numbering
                    last_number = 0
                    for existing_product in existing_products:
                        parts = existing_product.default_code.split('-')
                        if len(parts) > 1 and parts[1].isdigit():
                            number = int(parts[1])
                            last_number = max(last_number, number)

                    # Generate template default_code
                    template.default_code = f"{category_code}-{last_number + 1}"

                # Generate variant code if attributes exist
                attribute_values = product.product_template_attribute_value_ids
                variant_code = ''
                if attribute_values:
                    first_attribute = attribute_values[0]
                    variant_code = ''.join(word[:2].upper() for word in first_attribute.name.split())

                # Combine template.default_code with variant_code
                if variant_code:
                    product.default_code = f"{template.default_code}-{variant_code}"
                else:
                    # No attributes: use the template default_code
                    product.default_code = template.default_code

        return products
