# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Website CMS",
    "summary": "CMS features",
    "version": "9.0.1.0.2",
    "category": "Website",
    "website": "https://odoo-community.org/",
    "author": "Simone Orsi - Camptocamp, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    'application': False,
    "depends": [
        'website',
    ],
    "data": [
        # security
        'security/groups.xml',
        'security/ir.model.access.csv',
        # data
        "data/page_types.xml",
        "data/media_categories.xml",
        # "data/form_settings.xml",
        # views
        "views/menuitems.xml",
        "views/cms_page.xml",
        "views/cms_redirect.xml",
        "views/cms_media.xml",
        "views/cms_media_category.xml",
        'views/website_menu.xml',
        # templates
        "templates/assets.xml",
        "templates/misc.xml",
        "templates/layout.xml",
        "templates/menu.xml",
        "templates/page.xml",
        "templates/sidebar.xml",
        "templates/form.xml",
    ],
    'external_dependencies': {
        'python': ['requests', ],
    },
}
