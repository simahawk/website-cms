# -*- coding: utf-8 -*-
# Copyright 2017 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': 'CMS Account Form',
    'summary': """Basic form for user's account.""",
    'version': '10.0.1.0.0',
    'license': 'LGPL-3',
    'author': 'Camptocamp,Odoo Community Association (OCA)',
    'depends': [
        'cms_form',
        'website_portal',
    ],
    'data': [
        'security/partner_access.xml',
    ],
    "external_dependencies": {
        'python': [
            'validate_email',
        ],
    },

}
