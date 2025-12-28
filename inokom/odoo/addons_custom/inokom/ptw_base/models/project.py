from odoo import api, fields, models

class HseProject(models.Model):
    _name = 'hse.project'
    _description = 'HSE Project'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Project Name', tracking=True)
    pic = fields.Many2one('res.partner', 'Project Owner', tracking=True)
    vendor = fields.Many2many('res.partner', 'project_partner_vendor_rel', domain=[('ptw_vendor', '=', True), ('is_company', '=', True)], tracking=True)
    partner_line = fields.Many2many('res.partner', 'project_partner_worker_rel', domain="[('parent_id', 'in', vendor)]", string="Worker Involve")
    ptw_line = fields.One2many('hse.ptw','project_id')
    status = fields.Selection(selection=[
        ('new', 'New'),
        ('ongoing', 'Ongoing'),
        ('done', 'Done'),
        ('cancel', 'Cancel'),
    ], string='Status', default="new", required=True, tracking=True)
    area = fields.Many2one('hse.area', 'Area')
    area_owner = fields.Many2one('res.partner', 'Area Owner', related="area.area_owner")


    def write(self, vals):
        """Update project_id in res.partner when partner_line changes."""
        res = super(HseProject, self).write(vals)

        if 'partner_line' in vals:
            for project in self:
                new_partners = project.partner_line
                old_partners = self.env['res.partner'].search([('project_id', 'in', project.id)])
                
                # Add project to new partners
                to_add = new_partners - old_partners
                if to_add:
                    to_add.write({'project_id': [(4, project.id)]})

                # Remove project from partners no longer in partner_line
                to_remove = old_partners - new_partners
                if to_remove:
                    to_remove.write({'project_id': [(3, project.id)]})

        if 'vendor' in vals:
            for project in self:
                new_vendors = project.vendor
                old_vendors = self.env['res.partner'].search([('company_project_id', 'in', project.id)])
                
                # Add project to new vendors
                to_add = new_vendors - old_vendors
                if to_add:
                    to_add.write({'company_project_id': [(4, project.id)]})

                # Remove project from vendors no longer linked
                to_remove = old_vendors - new_vendors
                if to_remove:
                    to_remove.write({'company_project_id': [(3, project.id)]})

        return res