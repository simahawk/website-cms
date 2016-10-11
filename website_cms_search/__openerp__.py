# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Website CMS Text Search",
    "summary": "Add search facilitites for CMS pages (website_cms)",
    "version": "9.0.1.0.0",
    "category": "Website",
    "website": "https://odoo-community.org/",
    "author": "Simone Orsi - Camptocamp, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    'application': False,
    "depends": [
        "base",
        'website_cms',
    ],
    "data": [
        "templates/assets.xml",
        "templates/search.xml",
    ],
}
