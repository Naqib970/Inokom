from odoo import api, fields, models

class HseArea(models.Model):
    _name = 'hse.area'
    _description = 'HSE Area'

    name = fields.Char('Name')
    area_owner = fields.Many2one('res.partner', 'Area Owner')