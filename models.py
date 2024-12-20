from odoo import models,fields,api


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
                category_code = template.categ_id.code if template.categ_id and template.categ_id.code else ''
                if category_code:
                    last_product = self.search([('default_code', 'like', f"{category_code}-%")], order="default_code desc", limit=1)
                    if last_product and last_product.default_code:
                        last_number = int(last_product.default_code.split('-')[-1])
                    else:
                        last_number = 0
                    template.default_code = f"{category_code}-{last_number + 1}"
        return templates


class CustomProductProduct(models.Model):
    _inherit = 'product.product'

    width = fields.Char()
    depth = fields.Char()
    height = fields.Char()

    dimension = fields.Char()
    cbm = fields.Char()

    @api.model_create_multi
    def create(self, vals_list):
        products = super(CustomProductProduct, self).create(vals_list)
        for product in products:
            if not product.default_code:
                template = product.product_tmpl_id

                # Ensure the template default_code is generated
                if not template.default_code:
                    category_code = template.categ_id.code if template.categ_id and template.categ_id.code else ''
                    if category_code:
                        last_product = template.search(
                            [('default_code', 'like', f"{category_code}-%")], 
                            order="default_code desc", 
                            limit=1
                        )
                        if last_product and last_product.default_code:
                            last_number = int(last_product.default_code.split('-')[-1])
                        else:
                            last_number = 0
                        template.default_code = f"{category_code}-{last_number + 1}"

                # Generate default_code for the variant
                if template.default_code:
                    attribute_values = product.product_template_attribute_value_ids

                    # Create abbreviation with two words, removing non-alphabetic characters
                    abbr = "".join(
                        "".join(filter(str.isalpha, av.attribute_id.name[:2].upper())) +
                        "".join(filter(str.isalpha, av.name[:2].upper()))
                        for av in attribute_values
                    )

                    # Ensure abbreviation exists and is unique
                    generated_code = f"{template.default_code}-{abbr}"
                    suffix = 1
                    while self.search([('default_code', '=', generated_code)], limit=1):
                        generated_code = f"{template.default_code}-{abbr}{suffix}"
                        suffix += 1

                    product.default_code = generated_code
        return products





