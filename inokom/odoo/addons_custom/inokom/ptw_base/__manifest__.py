# -*- coding: utf-8 -*-

{
    'name': 'HSE',
    'version': '1.0',
    'category': 'Customizations',
    'sequence': 1,
    'summary': 'HSE Management',
    'description': "",
    'website': '',
    'depends': ['base_setup','contacts', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'security/access_right.xml',
        'data/ir_sequence.xml',
        'data/ptw_data.xml',
        'reports/report_paperformat.xml',
        'reports/ptw_report.xml',
        'views/ptw.xml',
        'views/vendor_detail.xml',
        'views/project.xml',
        'views/res_partner.xml',
        'views/area.xml',
        'views/contact_views.xml',
        'views/app_menu.xml',
    ],
    'license': 'LGPL-3',
    'assets': {},
    'installable': True,
    'application': True,
    'auto_install': False
}
