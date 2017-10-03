# -*- coding: utf-8 -*-

from openerp import models, fields


class WebsiteConfigSettings(models.TransientModel):
    """Override website config model."""

    _inherit = "website.config.settings"

    filter_menu = fields.Selection(
        string='Menu Filter',
        related='website_id.filter_menu',
        help='Filter to determine which menu shows in the front-end'
    )
