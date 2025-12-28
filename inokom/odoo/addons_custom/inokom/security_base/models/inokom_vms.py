from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.http import request
from datetime import datetime

class InokomVMS(models.Model):
    _name = 'inokom.vms'
    _description = 'Inokom VMS'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Many2one('res.partner', 'Visitor Name', domain="[('is_company','=', False),('user_ids', '=', False)]")
    id_no = fields.Char('IC/Passport Number', related="name.id_no")
    vehicle_no = fields.Char('Vehicle number')
    host_name = fields.Many2one('res.partner', 'Host Name')
    visit_purpose = fields.Many2one('inokom.vms.purpose','Visit Purpose')
    expected_date = fields.Datetime('Expected Date')
    checkin_time = fields.Datetime('Checkin Time')
    checkout_time = fields.Datetime('Checkout Time')
    status = fields.Selection(selection=[
        ('submit', 'Submitted'),
        ('ongoing', 'Ongoing'),
        ('complete', 'Complete'),
        ('cancel', 'Cancel')
    ], string='Status', default="submit", required=True, tracking=True)

    # Attachment
    pdpa_file = fields.Binary('Personal Data Protection Act Agreement (PDPA)', filename="pdpa_filename")
    pdpa_filename = fields.Char('PDPA Filename')
    item_declaration = fields.One2many('inokom.vms.item', 'vms_id')
    host_declare_file = fields.Binary('Host Declaration Form', filename="host_declare_filename")
    host_declare_filename = fields.Char('Host Declaration Form Filename')
    
    def scan_user_detail(self):
        return {
            'name': 'Visitor Scan',
            'type': 'ir.actions.act_window',
            'res_model': 'inokom.vms.scan',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
            'views': [(False, 'form')],
            'views': [(self.env.ref('security_base.view_security_vms_scan_form').id, 'form')],
            'context': {'form_view_initial_mode': 'edit'},
        }

    def action_visitor_checkin(self):
        self.ensure_one()
        allow=True
        if self.visit_purpose.hse_induction_required:
            if not self.name.hse_induction_valid:
                raise ValidationError(_("PTW Validation Failed: The visitor does not have a valid Permit To Work (PTW)."))

        if self.visit_purpose.ptw_required:
            allow=False
            ptw_list = request.env['hse.ptw'].search([
                ('status', '=', 'approve'),
                ('vendor_id', '=', self.name.parent_id.id),
            ])

            for ptw in ptw_list:
                for line in ptw.employee_line:
                    if line.name.id == self.name.id:
                        allow=True

        if allow==False:
            raise ValidationError(_("The visitor does not have a valid Permit To Work. Please ensure a valid PTW is provided."))

        if not self.pdpa_file:
            raise ValidationError(_("The visitor has not submitted the Personal Data Protection Act Agreement (PDPA)."))

        self.write({
            "checkin_time":datetime.now(),
            "status":"ongoing"
        })

    def action_visitor_checkout(self):
        self.ensure_one()
        if not self.host_declare_file:
            raise ValidationError(_("The host has not submitted the Declaration Form. Please ensure submission before visitors left the premise."))

        self.write({
            "checkout_time":datetime.now(),
            "status":"complete"
        })

    def action_visitor_generate_pass(self):
        return "test"

class InokomVMSItem(models.Model):
    _name = 'inokom.vms.item'
    _description = 'Inokom VMS Item'

    name = fields.Char("Name")
    vms_id = fields.Many2one("inokom.vms")
    quantity = fields.Integer("Quantity", default=1)


class InokomVMSScan(models.Model):
    _name = 'inokom.vms.scan'
    _description = 'Inokom VMS Scan'

    name = fields.Char("Name")
    id_no = fields.Char("IC/Passport Number")

    def search_visitor(self):
        self.ensure_one()

        search_domain = []
        if self.name:
            search_domain.append(('name.name', 'ilike', self.name))
        if self.id_no:
            search_domain.append(('id_no', 'ilike', self.id_no))

        return {
            'name': _('Search Visitor Results'),
            'type': 'ir.actions.act_window',
            'res_model': 'inokom.vms',
            'view_mode': 'list,form',
            'domain': search_domain,
            'target': 'current',
            'views': [
                (self.env.ref('security_base.view_security_vms_list').id, 'list'),
                (self.env.ref('security_base.view_security_vms_form').id, 'form')
            ],
        }