# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.
from odoo import models


class ProductAttributeValue(models.Model):
    _inherit = "product.attribute.value"

    def get_attribute_values(self, name, attribute_id, auto_create=False):
        """
        Gives attribute value if found, otherwise creates new one and returns it.
        :param name: name of attribute value
        :param attribute_id:id of attribute
        :param auto_create: True or False
        :return: attribute values
        """
        attribute_values = self.search([('name', '=ilike', name), ('attribute_id', '=', attribute_id)])

        if not attribute_values and auto_create:
            return self.create(({'name': name, 'attribute_id': attribute_id}))

        return attribute_values
