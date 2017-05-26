# -*- coding: utf-8 -*-
# Copyright 2017 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).


{
    "name": "CMS Translate",
    "summary": "TODO",
    "version": "9.0.1.0.0",
    "category": "Website",
    "website": "https://odoo-community.org/",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "license": "LGPL-3",
    "installable": True,
    'application': False,
    "depends": [
        'cms_form',
        'cms_page',
    ],
    "data": [
    ],
    'external_dependencies': {
        'python': ['requests', ],
    },
}
