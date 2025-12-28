from odoo import api, fields, models, _
from datetime import timedelta, datetime

class HsePtw(models.Model):
    _name = 'hse.ptw'
    _description = 'HSE PTW'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Reference Number', readonly=True, copy=False, index=True, default=lambda self: _('New'))
    status = fields.Selection(selection=[
        ('new', 'New'),
        ('pending', 'Pending Approval'),
        ('pending_hse', 'Pending HSE Approval'),
        ('approve', 'Approved'),
        ('reject', 'Reject'),
        ('hold', 'Hold'),
        ('complete', 'Complete'),
    ], string='Status', default="new", required=True, tracking=True)
    vendor_id = fields.Many2one('res.partner', 'Permit Issuer Company', domain="[('is_company','=',True),('ptw_vendor','=',True)]")
    project_id = fields.Many2one('hse.project', domain="[('vendor','in', vendor_id)]")
    project_owner = fields.Many2one('res.partner', 'Project Owner', related='project_id.pic')
    permit_issuer = fields.Many2one('res.partner', domain="[('parent_id', '=', vendor_id)]")
    permit_id_no = fields.Char('Identification Number', related='permit_issuer.id_no')
    permit_function = fields.Char('Permit Issuer Position', related='permit_issuer.function')
    permit_email = fields.Char('Permit Issuer Email', related='permit_issuer.email')
    permit_date = fields.Datetime(string='Date Application', default=lambda self: fields.Datetime.now())
    permit_valid_until = fields.Datetime(string='Date Valid Until', compute="_compute_permit_valid_until")
    area = fields.Many2one('hse.area', 'Location of Work', related='project_id.area')
    area_owner = fields.Many2one('res.partner', 'Area owner', related='area.area_owner')
    work_type = fields.Selection(selection=[
        ('external', 'External'),
        ('internal', 'Internal'),
        ('services', 'Services'),
        ('supplier', 'Supplier')
    ], string='Type of Work', required=True, tracking=True)

    employee_line = fields.One2many('hse.ptw.employee.line', 'ptw_id')
    tool_equipment = fields.One2many('hse.ptw.tool.line', 'ptw_id')

    project_owner_approve = fields.Boolean('Project Owner Approve')
    project_owner_approve_date = fields.Datetime('Project Owner Approve Date')
    area_owner_approve = fields.Boolean('Area Owner Approve')
    area_owner_approve_date = fields.Datetime('Area Owner Approve Date')
    hse_approve = fields.Boolean('HSE Department Approve')
    hse_approve_date = fields.Datetime('HSE Department Approve Date')

    # Application
    general_section = fields.Boolean('General Section', compute="_compute_section")
    general_score = fields.Float('General Score')
    description_of_work_general = fields.Text('DESCRIPTION OF WORK')
    gantt_chart_general = fields.Binary('GANTT CHART')

    machine_section = fields.Boolean('Machine Section', compute="_compute_section")
    machine_score = fields.Float('Machine Score')
    hiradc_machine = fields.Binary('HIRADC/JSA')
    license_machine = fields.Binary('OPERATOR DRIVING LICENSE/CERTIFICATE')
    inspection_checklist_machine = fields.Binary('EQUIPMENT INSPECTION CHECKLIST')
    ppe_checklist_machine = fields.Binary('PPE INSPECTION CHECKLIST')

    def _compute_section(self):
        for rec in self:
            if rec.general_score >= 80:
                rec.general_section = True
            else:
                rec.general_section = False

            if rec.machine_score >= 80:
                rec.machine_section = True
            else:
                rec.machine_section = False

    # hse control section
    logout_tagout_cm = fields.Boolean('Logout Tagout Control Measures')
    hot_work_cm = fields.Boolean('Hot Work Control Measures')
    confined_space_cm = fields.Boolean('Confined Space Control Measures')
    work_height_cm = fields.Boolean('Working At Height Control Measures')
    lift_activity_cm = fields.Boolean('Lifting Activity Control Measures')
    machine_control_cm = fields.Boolean('Machinery Control Measures')
    hazard_prevent_cm = fields.Boolean('Hazardous Prevention Control Measures')
    scheduled_waste_cm = fields.Boolean('Scheduled Waste Control Measures')
    demolation_cm = fields.Boolean('Demolition/Hacking Control Measures')
    excavation_prevent_cm = fields.Boolean('Excavation Prevention Control Measures')
    other_cm = fields.Char('Other Control Measures')

    head_protect = fields.Boolean('Head Protection')
    hand_protect = fields.Boolean('Hand Protection')
    eye_protect = fields.Boolean('Eye Protection')
    face_protect = fields.Boolean('Face Protection')
    foot_protect = fields.Boolean('Foot Protection')
    respiratory_protect = fields.Boolean('Respiratory Protection')
    hearing_protect = fields.Boolean('Hearing Protection')
    body_protect = fields.Boolean('Body Protection')
    fall_prevent_protect = fields.Boolean('Fall Prevention Protection')
    other_protect = fields.Char('Other Protection')

    def action_view_inspect_checklist(self):
        self.ensure_one()
        return {
            'name': _('Inspection'),
            'type': 'ir.actions.act_window',
            'view_mode': 'list,form',
            'res_model': 'hse.ptw.inspection',
            'domain': [('ptw_id', '=', self.id)],
            'context': {},
            'target': 'current',
        }

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'inokom.ptw.seq') or _('New')
        return super(HsePtw, self).create(vals)
    
    def write(self, vals):
        result = super().write(vals)
        for rec in self:
            if 'project_owner_approve' in vals:
                if rec.area_owner_approve:
                    rec.write({
                        'status':'pending_hse'
                    })

            if 'area_owner_approve' in vals:
                if rec.project_owner_approve:
                    rec.write({
                        'status':'pending_hse'
                    })

        return result 

    @api.depends('permit_date')
    def _compute_permit_valid_until(self):
        for rec in self:
            if rec.permit_date:
                rec.permit_valid_until = rec.permit_date + timedelta(days=7)
            else:
                rec.permit_valid_until = False

    def action_submit(self):
        for rec in self:
            rec.write({
                'status': 'pending'
            })

            project_owner = self.env["hse.project"].sudo().search([("id", "=", rec.project_id.id)], limit=1)

            if not project_owner:
                continue

            activity_id = self.env['mail.activity'].sudo().create({
                'res_model_id': self.env.ref('ptw_base.model_hse_ptw').id,
                'res_id': rec.id,
                'activity_type_id': self.env.ref('ptw_base.mail_act_ptw_reminder').id,
                'date_deadline': rec.permit_date.date() + timedelta(days=1),
                'summary': rec.name,
                'create_uid': self.env.user.id,
                'user_id': project_owner.pic.user_ids[0].id,
            })

            activity_id = self.env['mail.activity'].sudo().create({
                'res_model_id': self.env.ref('ptw_base.model_hse_ptw').id,
                'res_id': rec.id,
                'activity_type_id': self.env.ref('ptw_base.mail_act_ptw_reminder').id,
                'date_deadline': rec.permit_date.date() + timedelta(days=1),
                'summary': rec.name,
                'create_uid': self.env.user.id,
                'user_id': project_owner.area_owner.user_ids[0].id,
            })

    def action_approve(self):
        for rec in self:
            project_owner = self.env["hse.project"].sudo().search([("id", "=", rec.project_id.id)], limit=1)
            if self.env.user.id == project_owner.pic.user_ids[0].id:
                activity_id = self.env["mail.activity"].sudo().search([("res_model_id", "=", self.env.ref('ptw_base.model_hse_ptw').id),("res_id", "=", rec.id),("user_id", "=", self.env.user.id)], limit=1)
                if activity_id:
                    activity_id.action_feedback(feedback="Project Owner Appove Successfully")

                rec.write({
                    'project_owner_approve': True,
                    'project_owner_approve_date': datetime.now()
                })
                
            if self.env.user.id == project_owner.area_owner.user_ids[0].id:
                activity_id = self.env["mail.activity"].sudo().search([("res_model_id", "=", self.env.ref('ptw_base.model_hse_ptw').id),("res_id", "=", rec.id),("user_id", "=", self.env.user.id)], limit=1)
                if activity_id:
                    activity_id.action_feedback(feedback="Area Owner Appove Successfully")

                rec.write({
                    'area_owner_approve': True,
                    'area_owner_approve_date': datetime.now()
                })
    
    def action_hse_approve(self):
        for rec in self:
            rec.write({
                'status': 'approve',
                'hse_approve': True,
                'hse_approve_date': datetime.now()
            })

    def action_hse_reject(self):
        for rec in self:
            rec.write({
                'status': 'reject',
                'project_owner_approve': False,
                'project_owner_approve_date': False,
                'area_owner_approve': False,
                'area_owner_approve_date': False,
                'hse_approve': False,
                'hse_approve_date': False,
            })

    def action_hse_hold(self):
        for rec in self:
            rec.write({
                'status': 'hold',
            })

class HsePtwEmployeeLine(models.Model):
    _name = 'hse.ptw.employee.line'
    _description = 'HSE PTW Employee Line'

    ptw_id = fields.Many2one('hse.ptw')
    vendor_id = fields.Many2one('res.partner', related='ptw_id.vendor_id', store=True)
    name = fields.Many2one('res.partner', 'Employee Name', domain="[('parent_id','=',vendor_id)]")
    ic_passport = fields.Binary('IC/Passport', related='name.ic_passport', filename="ic_passport_filename")
    ic_passport_filename = fields.Char('filename', related='name.ic_passport_filename')
    work_permit = fields.Binary('Work Permit', related='name.work_permit', filename="work_permit_filename")
    work_permit_filename = fields.Char('filename', related='name.work_permit_filename')
    cidb_green = fields.Binary('CIDB Green Card', related='name.cidb_green', filename="cidb_green_filename")
    cidb_green_filename = fields.Char('filename', related='name.cidb_green_filename')

class HsePtwToolLine(models.Model):
    _name = 'hse.ptw.tool.line'
    _description = 'HSE PTW Tool Line'

    ptw_id = fields.Many2one('hse.ptw')
    name = fields.Char('Tool / Equipment Name')

class HsePtwInspection(models.Model):
    _name = 'hse.ptw.inspection'
    _description = 'HSE PTW Inspection'

    ptw_id = fields.Many2one('hse.ptw')
    name = fields.Char('Inspection Ref No')