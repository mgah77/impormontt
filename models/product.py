from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    type = fields.Selection(selection_add=[],
        default='product', track_visibility='onchange')

