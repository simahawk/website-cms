# Copyright 2018 Simone Orsi - Camptocamp
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    "name": "CMS statechart",
    "summary":
        """Add statechart to CMS world.""",
    "version": "11.0.1.0.0",
    "category": "Website",
    "website": "https://github.com/OCA/website-cms",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "license": "LGPL-3",
    "installable": True,
    "depends": [
        'cms_info',
        'statechart',
        'statechart_display_state',
        'fluxdock_project',
    ],
    "data": [
        'data/statechart.xml',
        'data/statechart_display_state.xml',
    ],
}
