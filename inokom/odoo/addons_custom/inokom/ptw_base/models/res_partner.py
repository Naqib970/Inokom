from odoo import api, fields, models
from datetime import date

class ResPartner(models.Model):
    _inherit = 'res.partner'

    ptw_vendor = fields.Boolean('PTW Vendor')
    department = fields.Many2one('inokom.department')
    project_id = fields.Many2many('hse.project', 'partner_project_worker_rel', 'Project')
    company_project_id = fields.Many2many('hse.project', 'partner_project_vendor_rel', 'Project')
    hse_induction_valid = fields.Boolean('HSE Induction Validity', compute="_compute_hse_induction_valid")
    hse_induction_expired = fields.Date('HSE Induction Expired Date')
    ptw_line = fields.One2many('hse.ptw', 'vendor_id')
    id_no = fields.Char('IC/Passport Number')
    ic_passport = fields.Binary('IC/Passport', filename="ic_passport_filename")
    ic_passport_filename = fields.Char('filename')

    work_permit = fields.Binary('Work Permit', filename="work_permit_filename")
    work_permit_filename = fields.Char('filename')

    cidb_green = fields.Binary('CIDB Green Card', filename="cidb_green_filename")
    cidb_green_filename = fields.Char('filename')

    @api.depends('hse_induction_expired')
    def _compute_hse_induction_valid(self):
        for record in self:
            if record.hse_induction_expired:
                record.hse_induction_valid = record.hse_induction_expired > date.today()
            else:
                record.hse_induction_valid = False

    def write(self, vals):
        res = super(ResPartner, self).write(vals)
        
        if 'project_id' in vals:
            for partner in self:
                new_projects = partner.project_id
                old_projects = self.env['hse.project'].search([('partner_line', 'in', partner.id)])

                # Add partner to new projects
                new_to_add = new_projects - old_projects
                if new_to_add:
                    new_to_add.write({'partner_line': [(4, partner.id)]})

                # Remove partner from old projects no longer linked
                to_remove = old_projects - new_projects
                if to_remove:
                    to_remove.write({'partner_line': [(3, partner.id)]})

        if 'company_project_id' in vals:
            for partner in self:
                new_projects = partner.company_project_id
                old_projects = self.env['hse.project'].search([('vendor', 'in', partner.id)])
                
                # Add vendor to new projects
                to_add = new_projects - old_projects
                if to_add:
                    to_add.write({'vendor': [(4, partner.id)]})

                # Remove vendor from projects no longer linked
                to_remove = old_projects - new_projects
                if to_remove:
                    to_remove.write({'vendor': [(3, partner.id)]})
                    
        return res