from odoo import fields, models, api


class ResPartner(models.Model):
    _inherit = 'res.partner'
    _rec_names_search = ['name', 'phone', 'email']              # The first way to search for a customer by phone number

                                                                # The second way to search for a customer by phone number
    # @api.model
    # def _name_search(self, name, domain=None, operator='ilike', limit=None, order=None):
    #     domain += ['|', ('name', operator, name), ('email', operator, name), ('phone', operator, name)]
    #     return  super()._name_search(name, domain, operator, limit, order)

