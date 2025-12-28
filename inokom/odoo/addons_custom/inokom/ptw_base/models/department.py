from odoo import api, fields, models

class InokomDepartment(models.Model):
    _name = 'inokom.department'
    _description = 'Inokom Department'

    name = fields.Char('Department')
    hod = fields.Many2one('res.partner', string='Department Head')
    manager = fields.Many2many('res.partner', string='Department Manager')