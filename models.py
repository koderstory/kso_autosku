from odoo import models,fields,api,exceptions


class CustomProductTemplate(models.Model):
    _inherit = 'product.template'

    width = fields.Char()
    depth = fields.Char()
    height = fields.Char()

    dimension = fields.Char()
    cbm = fields.Char()

    # default_code = fields.Char(readonly=True)

    # @api.model_create_multi
    # def create(self, vals_list):
    #     templates = super(CustomProductTemplate, self).create(vals_list)
    #     for template in templates:
    #         if not template.default_code:
    #             category_code = template.categ_id.code if template.categ_id and template.categ_id.code else ''
    #             if category_code:
    #                 last_product = self.search([('default_code', 'like', f"{category_code}-%")], order="default_code desc", limit=1)
    #                 if last_product and last_product.default_code:
    #                     last_number = int(last_product.default_code.split('-')[-1])
    #                 else:
    #                     last_number = 0
    #                 template.default_code = f"{category_code}-{last_number + 1}"
    #     return templates

    default_code = fields.Char(readonly=False)  # Allow editing, not required at field level

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('default_code'):
                vals['default_code'] = self._generate_default_code(vals)
        return super(CustomProductTemplate, self).create(vals_list)

    def write(self, vals):
        if 'default_code' in vals and not vals['default_code']:
            raise exceptions.ValidationError("Default Code cannot be empty during updates.")
        return super(CustomProductTemplate, self).write(vals)

    @api.constrains('default_code')
    def _check_default_code(self):
        for record in self:
            if not record.default_code:
                raise exceptions.ValidationError("Default Code is required.")

    def _generate_default_code(self, vals):
        """Generate a default_code based on category or other logic."""
        category_code = self.env['product.category'].browse(vals.get('categ_id')).code if vals.get('categ_id') else ''
        if category_code:
            last_product = self.search([('default_code', 'like', f"{category_code}-%")], order="default_code desc", limit=1)
            if last_product and last_product.default_code:
                last_number = int(last_product.default_code.split('-')[-1])
            else:
                last_number = 0
            return f"{category_code}-{last_number + 1}"
        else:
            raise exceptions.ValidationError("This product has category that doesn't has code. Category code is required to auto-generate a default code.")



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

                    # Create abbreviation with only attribute value, 2 characters per word, separated by '-'
                    abbr = "-".join(
                        f"{''.join(filter(str.isalpha, ''.join(word[:2].upper() for word in av.name.split())))}"
                        for av in attribute_values
                    )

                    # Ensure abbreviation exists and is unique
                    generated_code = f"{template.default_code}-{abbr}"
                    suffix = 1
                    while self.search([('default_code', '=', generated_code)], limit=1):
                        generated_code = f"{template.default_code}-{abbr}{suffix}"
                        suffix += 1

                    product.default_code = generated_code.upper()
        return products




