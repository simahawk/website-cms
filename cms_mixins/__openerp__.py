# -*- coding: utf-8 -*-
# Copyright 2017 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    "name": "CMS Mixins",
    "summary": "CMS features",
    "version": "9.0.1.0.0",
    "category": "Website",
    "website": "https://odoo-community.org/",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "license": "LGPL-3",
    "installable": True,
    'application': False,
    "depends": [
        'website',
    ],
    # TODO: include this conditionally
    "data": [
        'test_ir_rules_example.xml',
        'test_ir_model_access.xml',
    ],
    'external_dependencies': {
        'python': ['requests', ],
    },
}
