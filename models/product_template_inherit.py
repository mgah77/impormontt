from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    margin_calc = fields.Float("Margen")

    @api.onchange("standard_price", "margin_calc")
    def onchange_list_price_custom(self):
        if self.standard_price or self.margin_calc:
            marg = self.standard_price * self.margin_calc / 100
            list_price = self.standard_price + marg
            product_obj = self.env["product.template"].sudo().search([("name", "=", self.name)])
            if product_obj:
                product_obj.write({
                    "list_price": list_price,
                    "lst_price": list_price
                })
        else:
            self.list_price = False
            self.lst_price = False

    @api.model
    def create(self, vals):
        res = super(ProductTemplate, self).create(vals)
        if res.standard_price and res.margin_calc:
            marg = res.standard_price * res.margin_calc / 100
            list_price = res.standard_price + marg
            res.update({
                "list_price": list_price,
                "lst_price":list_price
            })
        return res
