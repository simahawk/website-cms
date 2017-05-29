# Copyright 2018 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).


from odoo import models, fields, api


class CMSContentMixin(models.AbstractModel):
    """Base model of a CMS content."""

    _name = 'cms.content.mixin'
    _description = 'CMS content mixin'
    _inherit = [
        'website.published.mixin',
        'cms.orderable.mixin',
        'cms.coremetadata.mixin',
    ]

    name = fields.Char(
        'Name',
        required=True,
    )
    description = fields.Text(
        'Description',
        help="Brief description of what this content is about."
    )
    body = fields.Html(
        'HTML Body',
        sanitize=False
    )

    @api.multi
    def toggle_published(self):
        """Publish / Unpublish this page right away."""
        self.write({'website_published': not self.website_published})
