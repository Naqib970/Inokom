# -*- coding: utf-8 -*-

{
    'name': 'Security',
    'version': '1.0',
    'category': 'Customizations',
    'sequence': 1,
    'summary': 'Security Management',
    'description': "",
    'website': '',
    'depends': ['base_setup','contacts', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'security/access_right.xml',
        'views/visit_purpose.xml',
        'views/vms.xml',
        'views/app_menu.xml',
    ],
    'license': 'LGPL-3',
    'assets': {},
    'installable': True,
    'application': True,
    'auto_install': False
}
