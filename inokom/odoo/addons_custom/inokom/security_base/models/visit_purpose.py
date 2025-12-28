from odoo import api, fields, models
import qrcode
import base64
from io import BytesIO

class InokomVMSPurpose(models.Model):
    _name = 'inokom.vms.purpose'
    _description = 'Inokom VMS Purpose'

    name = fields.Char('Visit Purpose')
    hse_induction_required = fields.Boolean('Require HSE Induction')
    ptw_required = fields.Boolean('Require PTW')
    qr_code_registration = fields.Boolean('QR Code Registration')
    qr_code = fields.Binary(string='QR Code', copy=False, compute="_compute_qr_code")

    def _compute_qr_code(self):
        for rec in self:
            if not rec.qr_code_registration:
                rec.qr_code = False
            else:
            # define the QR Code
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=10,
                    border=4,
                )
                # generate the URL
                qr_url = ''+ rec.env['ir.config_parameter'].sudo().get_param('web.base.url')
                # qr_url = '/get_in_touch/' +
                # + str(rec.id)

                # add the url to QR
                qr.add_data(qr_url)
                qr.make(fit=True)

                # convert QR Code to Image
                img = qr.make_image()
                temp = BytesIO()
                img.save(temp, format="JPEG")
                qr_image = base64.b64encode(temp.getvalue())

                # save the image
                rec.update({'qr_code': qr_image})